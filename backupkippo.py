#!/usr/bin/env python3
# -*- coding: utf-8 -*-




import schedule
import time
import paramiko
import xml.etree.cElementTree as xec
import getpass


def dosyaindir():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('ip adress', username="kullanıcı adı", password=kpass, key_filename=kpath) #SSH bilgilerini giriyoruz.
    #ssh.connect('ip adress', username="kullanıcı adı", password='Password') #Parola ile giriş için bu komutu kullanabilirsiniz üstekini iptal ediniz. 
    sftp = ssh.open_sftp()
    localpath = lyer+'kippo.log'   
    remotepath = 'sunucudaki log dosyasının yeri'
    sftp.get(remotepath,localpath)
    sftp.close()
    ssh.close()
    okuyucu()  

def control(satir):
    splitsatir = satir.split()  #File Parseling Yapmak için Belli Bir kural oluşturdum aşağıda. Okuyucudan aldığı her satırı boşluktan bölüp belli sorgulara sokuyor
    if(len(splitsatir) == 9 and splitsatir[3] == 'New' and splitsatir[4] == 'connection:' ):
        print("==============================")
        print("Saldırı Başladı!!!")
        splitsession = splitsatir[8].split("]")   #Normalde boşluğa göre kestiği için session id'yi alamıyorduk. Bu split ile alabiliyoruz.
        print("Session id:",splitsession[0])
        print("Tarih:",splitsatir[0])
        print("Saat:",splitsatir[1])
        global sid  #XML'deki ağaç yapısı için. Session Id'nin altına alabilmemiz için değer atamam lazım. Değere ulaşmak içinde global variable kullandık
        sid = xec.SubElement(doc,"Session {}".format(splitsession[0]))
        xec.SubElement(sid,"Tarih").text = splitsatir[0]
        xec.SubElement(sid,"Saat").text = splitsatir[1]
    elif(len(splitsatir) > 5 and splitsatir[3] == 'Remote' and splitsatir[4] == 'SSH'):
        print("SSH Version",splitsatir[6:])
        xec.SubElement(sid,"SSH").text = str(splitsatir[6:])
    elif(len(splitsatir) == 10 and splitsatir[6] == 'login' and splitsatir[7] == 'attempt'):
        print("Sözlük Saldırısı:",splitsatir[8])
        print("Başarı Durumu:",splitsatir[9])
        xec.SubElement(sid,"Sozluk Saldirisi").text = splitsatir[8]
        global durum
        durum = xec.SubElement(sid,"Basari Durumu {}".format(splitsatir[8]))
    elif(len(splitsatir) == 5 and splitsatir[3] == 'connection' and splitsatir[4] == 'lost'):
        print("Bağlantı Koptu",splitsatir[1])
        xec.SubElement(sid,"Baglanti Koptu").text = splitsatir[1]
    elif(len(splitsatir) > 10 and splitsatir[2] == '[SSHChannel' and splitsatir[10] == 'CMD:'):
        print("Girilen Komut:",splitsatir[11:])
        a=str(splitsatir[11:])
        global kmt
        kmt = xec.SubElement(durum,"Komut",deger=a)
    elif(len(splitsatir) > 10 and splitsatir[10] == 'Command' and splitsatir[11] == 'found:'):
        print("Komut Başarılı:",splitsatir[1])
        xec.SubElement(kmt,"Durum",deger="Basarili").text = splitsatir[1]
    elif(len(splitsatir) > 10 and splitsatir[10] == 'Command' and splitsatir[11] == 'not'):
        print("Komut Başarısız:",splitsatir[1])
        xec.SubElement(kmt,"Durum",deger="Basarisiz").text = splitsatir[1]

      
def okuyucu():    
    logfile = open(lyer+"kippo.log","r")  #İndirilen dosyanın yerini açmak için. r = reading mode
    for i in logfile:    
        control(i) #Alınan her satırı teker teker control adını verdiğimiz fonksiyona gönderiliyor
    logfile.close()
    
    
def xmlyaz():
    global doc
    root = xec.Element("root")
    doc = xec.SubElement(root,"Saldirilar")
    dosyaindir()  #XML'in ilk bilgilerini verip yapıyı yavaş yavaş oluşturuyoruz. Sonra da dosyaindir() fonksiyonuna geçiyoruz.
    tree = xec.ElementTree(root)
    tree.write(xmlyer+"kippo.xml")
        
print("🔥 Mücahit Çeri	🔥\nPath girerken lütfen sonuna / koyunuz 🙃\n")
lyer = input("Dosyanın kaydedileceği yer:")
xmlyer = input("XML'in kaydedileceği yer:")
kpath=input("Private Key Yolu:")
kpass=getpass.getpass("Key için Passphrase Giriniz:")
print("Program Başarıyla Çalışıyor...")
#schedule.every(1).minutes.do(xmlyaz)  #Hızlıca test etmek isterseniz diye buraya bırakıyorum bu kodu <3
schedule.every().day.at("saat:dakika").do(xmlyaz) #Her gün saat xx:xx'de backup yapması için girilen komut. xmlyaz fonksiyonunu saat gelince çalıştırıyor Saat formatı örneği: 04:30
while True:
    schedule.run_pending()
    time.sleep(1)
    


