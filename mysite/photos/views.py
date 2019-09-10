import time

from django.shortcuts import render, redirect
from django.http import JsonResponse

#from google.cloud import vision
import sys
import string
import pytesseract
from .forms import PhotoForm
from .models import Photo
import requests
import os
import json

from pdf2image import convert_from_path

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import difflib
import csv


import uuid 


from PIL import Image

from PIL import ImageEnhance, ImageFilter

from difflib import SequenceMatcher

from django.views import View


class BasicUploadView(View):
    def get(self, request):
        photos_list = Photo.objects.all()
        return render(self.request, 'photos/basic_upload/index.html', {'photos': photos_list})

    def post(self, request):
        form = PhotoForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            photo = form.save()
            data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


class ReadOcrGoogle(object):

    def __init__(self):
        self.variable="foo"
    
    def ReadOcrDataGoogle(url):
        google_vision_baseUrl="https://vision.googleapis.com/v1/images:annotate?key=AIzaSyAoUbR4olpLrpvvRmpLtFvCqtKmiI8i95g"
        uploaded_file_url_abs="http://documentparser.westus.cloudapp.azure.com" +url
        #uploaded_file_url_abs="http://127.0.0.1" +url
        print("url final")
        print(uploaded_file_url_abs)
        print("url ended")
        #uploaded_file_url_abs="G:/Document reading/Read_multiple Documents"+url
        #image_data=open(uploaded_file_url_abs,'rb').read()
        headers={'Content-Type':'application/octet-stream'}
        #http://documentparser.southcentralus.cloudapp.azure.com:81/media/photos/IMG_20160111_234032.jpg
        data={
            "requests":[
                {
                "image":{
                    "source":{
                    "imageUri":uploaded_file_url_abs
                    }
                },
                "features":[
                    {
                    "type":"TEXT_DETECTION"
                    }
                ]
                }
            ]
            }
        print("6")
        response=requests.post(url=google_vision_baseUrl,headers=headers,data=json.dumps(data))
        print("7")
        response.raise_for_status()
        ocrdata = response.json()
        

        json_ocrdata=""
        try:
            json_ocrdata=((ocrdata["responses"])[0]["fullTextAnnotation"]["text"])
            
        except:
            print(ocrdata)
        #print(ocrdata)
        #print((ocrdata["responses"])[0]["fullTextAnnotation"]["text"])
        #json_ocrdata=((ocrdata["responses"])[0]["fullTextAnnotation"]["text"])
        
        print("ocr data printin")
        print(json_ocrdata)
        print("ocr data end")
        alldata=[]   
        #pan card
        if json_ocrdata.find("INCOME")>=0 or json_ocrdata.find("GOVT")>=0 or json_ocrdata.find("Permanent")>=0 :
            #print("Pan Entered----->>")
            alldata=json_ocrdata.splitlines()
            
            
            dob=""
            name=""
            fname=""
            pan=""

            test_data=['INCOME','GOVT','INDIA','DEPART','INDA','Account','Permanent','Signature','sign']

            for td in test_data:
                for line_data in alldata:
                    if(line_data.find(td)>=0):
                        alldata.remove(line_data)


             
            print(alldata)
            

            for st in alldata:
                if "/" in st :
                    dob=st
                    print(dob)
                    
                    alldata.remove(st)
                    break
            for st in alldata:
                    
                if len(st)==10 and st[0:5].isalpha() and st[5:8].isdigit() and st[9].isalpha:
                    pan=st
                    print(st)
                    
                    alldata.remove(st)
                    break
                    
            
            print("last data")
            print(alldata)
            
            if(len(alldata)>2):
                if(re.match("^[A-Za-z _-]*$",alldata[0])):
                    name=alldata[0]
                    fname=alldata[1]
                elif(re.match("^[A-Za-z _-]*$",alldata[1])):
                    name=alldata[1]
                    fname=alldata[2]

            elif(len(alldata)==2):
                name=alldata[0]
                fname=alldata[1]
            
            return_data="PAN Card</p></td><td><p><b>Name : </b>"+name+"<br/><b>Father's name : </b>"+fname+"<br/><b>DOB : </b>"+dob+"<br/><b>PAN : </b>"+pan+"</p></td></tr>"
            """ mail_the_data=mailData()
            mail_the_data.mail_Data(url,return_data,"Google") """
            return return_data

        #USDL
        elif(json_ocrdata.find("DRIVING") or json_ocrdata.find("LICENCE") or json_ocrdata.find("Licencing") ):
            print("DL")
            alldata=json_ocrdata.splitlines()
            DLNumber=""
            pName=""
            fName=""
            junk_data=['INDIAN','DRIVING',"lICENCING",'RTA' ]
            image_des="DL Detected"
            for jd in junk_data:
                for ld in alldata:
                    alldata.remove(ld)
            
            return image_des

        #Aadhar card
        elif (json_ocrdata.find('Government')>=0 or json_ocrdata.find('Birth')>=0 or json_ocrdata.find('DOB')>=0 or json_ocrdata.find('India')>=0 or json_ocrdata.find('Male')>=0 or json_ocrdata.find('Female')>=0) and (json_ocrdata.find('Bank')==-1) :
            #print("aadhar entered ---->>>>>")
            alldata=json_ocrdata.splitlines()
            aadhar=""
            name=""
            dob=""
            gender=""

            test_data=['GOVERNMENT','Government','INDIA','DEPART','INDA']

            for td in test_data:
                for line_data in alldata:
                    if(line_data.find(td)>=0):
                        alldata.remove(line_data)


            aadhar_re=re.compile('^\d{4}\s\d{4}\s\d{4}$')
            for st in alldata:
                if re.match(aadhar_re,st) is not None:
                    aadhar=st
                    print(st)
                    
                    alldata.remove(st)
                    break
            for st in alldata:
                if "/" in st :
                    dob=st.split(':',1)[-1]
                    print(dob)
                    
                    alldata.remove(st)
                    break
                if ([w for w in st if re.search('(Year|Birth|Birth:|irth|YoB|YOB:|DOB:|DOB|DoB)$', w)]):
                    bt=st.split(':',1)[-1]
                    #if(st.find(':')>=0):
                        

                    dob=bt
                    print('dob is')
                    print(dob)
                    alldata.remove(st)
                    break
            for st in alldata:
                if ([w for w in st if re.search('(Female|Male|emale|male|ale|FEMALE|MALE|EMALE)$', w)]):
                    gender=st
                    print(gender)

                    alldata.remove(st)
                    break
            
            print(alldata)

            if(len(alldata)>1):
                if(re.match("^[A-Za-z _-]*$",alldata[0])):
                    name=alldata[0]
                else:
                    name=alldata[1]
            elif(len(alldata)==1):
                name=alldata[0]


            return_data="Aadhar Card</p></td><td><p><b>Name : </b>"+name+"<br/><b>DOB : </b>"+dob+"<br/><b>Gender : </b>"+gender+"<br/><b>Aadhar : </b>"+aadhar+"</p></td></tr>"
            """ mail_the_data=mailData()
            mail_the_data.mail_Data(url,return_data,"Google") """
            return return_data
        elif(json_ocrdata.find('Bank')>=0 or json_ocrdata.find('IFSC')>=0):
            if(json_ocrdata.find('SBI')>=0 or json_ocrdata.find('SBIN')>=0):

                #nothing
                print("Bank")
                bank_name=""
                statement_period=""
                AccNO=""
                branch_name=""
                Acc_type=""
                Acc_name=""
                Acc_balance=""
                bank_ifsc=""
                json_ocrdata=json_ocrdata.splitlines()
                
                bal_index=[json_ocrdata.index(i) for i in json_ocrdata if 'Balance as' in i]
                print(bal_index[0])
                json_ocrdata=json_ocrdata[0:bal_index[0]+2]
                print(json_ocrdata)
                for st in json_ocrdata:
                    
                    if st.lower().find("bank")>=0:
                        bank_name=st
                        print(bank_name)
                        json_ocrdata.remove(st)
                        break
                for st in json_ocrdata:
                    if("period") in st.lower():
                        
                        statement_period=st.split('period',1)[-1]
                        json_ocrdata.remove(st)
                        break
                for st in json_ocrdata:
                    if("account number" or "acc0unt number" ) in st.lower():
                        st_index=json_ocrdata.index(st)
                        AccNO=json_ocrdata[st_index+1]
                        json_ocrdata.remove(st)
                        json_ocrdata.remove(AccNO)
                        break
                for st in json_ocrdata:
                    if("branch") in st.lower():
                        st_index=json_ocrdata.index(st)
                        branch_name=json_ocrdata[st_index+1]
                        json_ocrdata.remove(st)
                        json_ocrdata.remove(branch_name)
                        break
                for st in json_ocrdata:
                    if("account type") in st.lower():
                        st_index=json_ocrdata.index(st)
                        Acc_type=json_ocrdata[st_index+1]
                        json_ocrdata.remove(st)
                        json_ocrdata.remove(Acc_type)
                        break
                for st in json_ocrdata:
                    if("account name") in st.lower():
                        st_index=json_ocrdata.index(st)
                        Acc_name=json_ocrdata[st_index+1]
                        json_ocrdata.remove(st)
                        json_ocrdata.remove(Acc_name)
                        break
                for st in json_ocrdata:
                    if("SBIN") in st:
                        bank_ifsc=st
                        json_ocrdata.remove(st)
                        break
                    
                
                Acc_balance=json_ocrdata[-1]
                print(json_ocrdata)

                image_des=bank_name+" </p></td><td><p><b>Name:</b> "+Acc_name+"<br/><b>Period:</b> "+statement_period+"<br/><b>Acc No:</b> "+AccNO+"<br/><b>Branch:</b> "+branch_name+"<br/><b>IFSC: </b>"+bank_ifsc+"<br/><b>Account Type: </b>"+Acc_type+"<br/><b>Balance: </b>"+Acc_balance+"</p></td>"
                """ mail_nodata=image_des+str(json_ocrdata)
                mail_the_data=mailData()
                mail_the_data.mail_Data(url,mail_nodata,"SBI Bank") """
                return image_des


            else:
                image_des="Unknown Bank</p></td><td><p>We are not currently serving your Bank. Get back soon</p></td>"
                """  mail_nodata=image_des+str(json_ocrdata)
                mail_the_data=mailData()
                mail_the_data.mail_Data(url,mail_nodata,"Bank") """
                return image_des
        else:
            print(json_ocrdata)
            image_des="Unable to detect</p></td><td><p>Please upload a clear Image</p></td>"
            """ mail_nodata=image_des+json_ocrdata
            mail_the_data=mailData()
            mail_the_data.mail_Data(url,mail_nodata,"Google") """
            return image_des
                 
        return alldata
        
class mailData(object):
    def __init__(self):
        self.variable="foo"
    
    def mail_Data(self,url,result,source):
        me='thrilokpyproject@gmail.com'
        you='trilokm@byteridge.com'

        
        server=smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login('thrilokpyproj@gmail.com','trilok1@E') 
        msg=MIMEMultipart('alternative')
        msg['subject']="py data extract "+source

        msg['From']=me
        msg['you']=you
        text="details captured"
        
        html_text="<table botder=\"1\"><tr><td><img src='"+url+"' height='100' alt='"+url+"'></img></td><td><p>"+result+"</table>"
        part1=MIMEText(text,'plain')
        part2=MIMEText(html_text,'html')
        msg.attach(part1)
        msg.attach(part2)

        server.sendmail("thrilokpyproj@gmail.com","trilokm@byteridge.com",msg.as_string())
        server.quit()


class ProgressBarUploadView(View):
    def get(self, request):
        photos_list = Photo.objects.all()
        return render(self.request, 'photos/progress_bar_upload/index.html', {'photos': photos_list})

    def post(self, request):
        #time.sleep(1)  # You don't need this line. This is just to delay the process so you can see the progress bar testing locally.
        form = PhotoForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            photo = form.save()
            st=photo.file.url
            ext=st.split('.',1)[-1]
            ext1=st.split('.',1)[0]
            
            print(ext1)
            image_des=""
            if(ext=="pdf"):
                abs_path="/home/trilok567/doc1/read_multiple_documents"+photo.file.url
                pages=convert_from_path(abs_path,500)
                final_img_url=""
                ustr=uuid.uuid4().hex[:6].upper()
                for page in pages:
                    final_img_url="/home/trilok567/doc1/read_multiple_documents/media/photos/bank_"+ustr+".jpg"
                    image_url="/media/photos/bank_"+ustr+".jpg"
                    print(final_img_url)
                    print("one")
                    page.save(final_img_url,'JPEG')
                    print(final_img_url)
                    print("1")
                    pass_on_image="http://documentparser.southcentralus.cloudapp.azure.com"+image_url
                    print("2")
                    
                    break
                print("3")
                image_des=ReadOcrGoogle.ReadOcrDataGoogle(image_url)
                print("4")
                data = {'is_valid': True, 'name': photo.file.name, 'url':image_url ,'img_data':image_des}
            else:
                image_des=ReadOcrGoogle.ReadOcrDataGoogle(photo.file.url)

                data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url,'img_data':image_des}

        else:
            image_des="Unable to detect</p></td><td><p>Please upload a clear Image</p></td>"
            data = {'is_valid': False}
        return JsonResponse(data)


class DragAndDropUploadView(View):
    def get(self, request):
        photos_list = Photo.objects.all()
        return render(self.request, 'photos/drag_and_drop_upload/index.html', {'photos': photos_list})

    def post(self, request):
        form = PhotoForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            photo = form.save()
            data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


def clear_database(request):
    for photo in Photo.objects.all():
        photo.file.delete()
        photo.delete()
    return redirect(request.POST.get('next'))
