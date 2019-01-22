# -*- coding: utf-8 -*-
import scrapy
import sys
import unittest, time, re
import urllib2
import StringIO
import csv
import logging
import pyperclip
import httplib
import math

from datetime import datetime,timedelta
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from psgrabr.items import ScrapyProjectItem
from scrapy.exceptions import CloseSpider
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.remote.remote_connection import LOGGER

from time import sleep

from webdriverdownloader import GeckoDriverDownloader #trying out this bad boy

'''
This spider will be used to make offers from Miami to Buenos Aires
This spider works without neither a GUI nor the need of inputting values during runtime

Predefined values:
- Account to be used (email, password)
- Annotation to attach for the offers to be made
- Origin and destination cities (Miami, Buenos Aires)
- Travel and deliver dates
- Number of scrolls
- Flag for updating our own offers

TODO add geckodriver to either requirements.txt or the other .yml file, now how tf do we do that god knows
'''

class GrabrSpider(CrawlSpider):
    name = "hlnewgr_ar"
    item_count = 0
    allowed_domains = ['grabr.io']
    start_urls = ['https://grabr.io/es/login']   #'https://grabr.io/es/travel/from/20044/to/15482' 'https://grabr.io/es/login'
    #start_urls = ['https://grabr.io/es/login']
    # rules = {
    #   Rule(LinkExtractor(allow = (), restrict_xpaths= ))
    # }

    def parse(self, response):
        LOGGER.setLevel(logging.WARNING)
        urllib3_log = logging.getLogger("urllib3")
        urllib3_log.setLevel(logging.CRITICAL)
        geckodriver = '.\\geckodriver\\geckodriver.exe' #attempt to include it within the project
        geckodriverRoot = '.\\geckodriver.exe' #attempt to include it within the project
        scraping_hub_bin_path = '/scrapinghub/bin'  #im not sure whether this is a good idea or just plain retarded but i sure hope it works kek
        scraping_hub_bin_path2 = '\\scrapinghub\\bin\\geckodriver.exe'
        scraping_hub_bin_path3 = '/scrapinghub/webdriver/gecko/v0.23.0/geckodriver-v0.23.0-linux64/geckodriver'
        scraping_hub_bin_path4 = '\\scrapinghub\\webdriver\\gecko\\v0.23.0\\geckodriver-v0.23.0-linux64\\geckodriver'
        print "Creating firefox options..."
        options = webdriver.FirefoxOptions()
        print "Firefox options created."
        print "Adding argument headless..."
        options.add_argument('-headless')
        print "-headless argument added to options"
        print "------------------------------------"
        try:
            print "Creating instance of GeckoDriverDownloader"
            gdd = GeckoDriverDownloader()
            print "Created instance of GeckoDriverDownloader"
        except Exception as e:
            print "Couldn't create instance of GeckoDriverDownloader class"
            sys.exit()

        try:
            print "Downloading and installing geckodriver"
            (new_path, _useless_garbage) = gdd.download_and_install()
            print "Downloaded and installed geckodriver"
            print new_path
        except Exception as e:
            print "Couldn't download and install geckodriver"
            sys.exit()
        TEST_RUN_FLAG = True

        fromCityOption=0
        toCityOption=0
        newAccountFlag = 0
        newAnnotationFlag=0

        username='harleen_vl@hotmail.com'
        password='w0mirnms'

        annotation = "Hola soy Luis y quisiera llevar tu producto"
        annotation = annotation.decode(sys.stdin.encoding)

        origin_city = "miami"
        destination_city = "buenos aires"

        raw_travel_date = "12/03/2019"
        raw_final_date = "18/03/2019"

        travelDate = self.makeDate(raw_travel_date)
        print "Travel date successfully assigned by makeDate"
        finalDate = self.makeDate(raw_final_date, travelDate)
        print "Final date successfully assigned by makeDate"

        fromCityName = origin_city
        toCityName = destination_city

        iterations = 1 #between 0 and 5000 (scrolls)

        isTravelSquad = 0 # travel squad no longer exists

        updatingAccepted = 1 #whether the program should try to update offers already made or not

        itera=0
        while True:
            basepath ='https://grabr.io/es'
            completedOffers=0
            editedOffers=0
            failedOffers=0

            stanleyOffers = 0
            funkoOffers = 0
            lolOffers = 0

            noEditFailedOffers=0
            noEditBetterPrice=0
            noEditLowerPrice=0
            editedByRecalibration=0
            zeroOffers = 0
            noEditSquadOffer = 0
            noEditByNoAuthorization = 0
            noEditStanleyItem = 0
            noEditFunkoItem = 0
            noEditLolItem = 0
            noEditUpdateForm = 0
            funkoItemsSuccess = 0

            failedNotExistAnymoreOffers = 0

            csv = open("itemsSinOfertas.csv", "w")
            encabezado = "nombreUsuarioComprador, nombreItem, precioBaseItem,urlOferta\n"
            csv.write(encabezado)

            csvFailed = open("itemsFallados.csv","w")
            encabezadoFailed = "nombreUsuarioComprador, nombreItem, urlOferta\n"
            csvFailed.write(encabezadoFailed)

            csvStanleys = open("items_stanley.csv", "w")
            encabezadoStanley = "urlOferta\n"
            csvStanleys.write(encabezadoStanley)

            csvFunkos = open("items_funko_pop.csv", "w")
            encabezadoFunko = "urlOferta\n"
            csvFunkos.write(encabezadoFunko)

            csvLols = open("items_lol.csv", "w")
            encabezadoLol = "urlOferta\n"
            csvLols.write(encabezadoLol)

            dias= iterations
            today = datetime.now()

            deltaDays = timedelta(days=(iterations+1))
            dateLimit = today - deltaDays

            dayLimit =dateLimit.day
            monthLimit = dateLimit.strftime("%B").lower()
            monthLimit = self.monthNameToSpanish(monthLimit)

            if itera==0:
                fromCityName = fromCityName.lower()
                toCityName = toCityName.lower()
                try:
                    # self.driver = webdriver.Firefox(executable_path=geckodriver, firefox_options=options)
                    # self.driver = webdriver.Firefox(executable_path=geckodriverRoot, firefox_options=options)
                    # print "Added geckodriver as argument from the root folder"
                    print "Adding geckodriver from the path of download:"
                    print scraping_hub_bin_path2
                    self.driver = webdriver.Firefox(executable_path=scraping_hub_bin_path2, firefox_options=options)
                    print "Added geckodriver from the path of download"
                except Exception as e:
                    print e
                    # print "Couldn't add geckodriver as argument"
                    print "Couldn't add geckodriver from the path of download"
                    # sys.exit()
                    print "Creating headless driver normally"
                    self.driver = webdriver.Firefox(firefox_options=options)
                    print "Headless webdriver created normally"
                self.driver.get(response.url)
                sleep(2)
                inputEmailElement = self.driver.find_element_by_xpath("//input[@type='email']")
                inputEmailElement.send_keys(username)
                inputPasswordElement = self.driver.find_element_by_xpath("//input[@type='password']")
                inputPasswordElement.send_keys(password)
                submitButton = self.driver.find_element_by_xpath("//button[@type='submit']")
                sleep(1)
                submitButton.click()
                sleep(1)
                try:
                    WebDriverWait(self.driver, 15).until(EC.text_to_be_present_in_element((By.XPATH, "//div[@id='app-root']"), "2"))
                except Exception as e:
                    print "No se pudo iniciar sesion"
                    break
                sleep(2.5)
                travelLink = self.driver.find_element_by_xpath("//a[@href='/travel']")
                sleep(2)
                travelLink.click()
                sleep(3)
                webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                #linea a revisar
                k=0
                while True:
                    try:
                        inputCityFrom = self.driver.find_element_by_xpath('//label[@class="fx-r ai-c cur-d pl15 input input--w w100p bdr5 bdw1 bdc-g12 bds-s MD_bdrr0 MD_bdbr0"]//input[@class="fxg1 miw0"]')
                        break
                    except Exception as e:
                        print "Mensaje de excepcion:" + str(e)
                        if k == 5:
                            sys.exit()
                        k=k+1
                        sleep(1)

                ###########
                inputCityFrom.send_keys(fromCityName)
                sleep(2)
                tam=0
                while True :
                    sleep(1)
                    fromCitiesList = self.driver.find_elements_by_xpath('//div[@class="link link--b lh1 px20 py15 cur-p ellipsis c-b trd300ms MD_bgc-g3-hf px20 py10 ws-nw ellipsis"]/span')
                    tam = (len(fromCitiesList))/2
                    if tam > 0:
                        print "Lista de ciudades origen"
                        print "------------------------------"
                        break
                    inputCityFrom.clear()
                    inputCityFrom.send_keys(fromCityName)

                for i,city in enumerate(fromCitiesList):
                    if i == tam:
                        "------------------------------"
                        break
                    print str(i+1)+ ") " + city.text

                fromCityOption = 1

                sleep(3)
                firstCityFrom =  fromCitiesList[fromCityOption-1]
                firstCityFrom.click()

                inputCityTo = self.driver.find_element_by_xpath('//label[@class="fx-r ai-c cur-d pl15 input input--w w100p mt10 bdr5 bdw1 bdc-g12 bds-s MD_bdls-n MD_bdlr0 MD_bdbr0 MD_mt0"]//input[@class="fxg1 miw0"]')
                inputCityTo.send_keys(toCityName)
                sleep(2)

                while True :
                    sleep(1)
                    toCitiesList = self.driver.find_elements_by_xpath('//div[@class="link link--b lh1 px20 py15 cur-p ellipsis c-b trd300ms MD_bgc-g3-hf px20 py10 ws-nw ellipsis"]')
                    tam = (len(toCitiesList))/2
                    if tam>0:
                        print "Lista de ciudades destino"
                        print "------------------------------"
                        break
                    inputCityTo.clear()
                    inputCityTo.send_keys(toCityName)

                for i,city in enumerate(toCitiesList):
                    if i == tam:
                        print "------------------------------"
                        break
                    print str(i+1)+") "+city.text

                toCityOption = 1

                firstCityTo =  toCitiesList[toCityOption-1]
                firstCityTo.click()

                sleep(1)
                searchButton = self.driver.find_element_by_xpath('//button[@class="button pos-r d-ib va-t btn fxs0 h50 w100p px30 mt10 bdr5 MD_mt0 MD_bdtr0 btn--bb"]/div')
                searchButton.click()
            print "empezamos la iteracion..."
            itera= itera+1

            sleep(2)
            try:
                print "esperamos a que cargue la página..."
                WebDriverWait(self.driver, 10).until(EC.text_to_be_present_in_element((By.XPATH, "//div[@id='app-root']"),"2"))
            except Exception as e:
                print "No se encontraron resultados"
                break

            limitElements=0
            count = 0
            message=""
            diff=0
            numberOfTimesBefore=0
            nn=0
            numOfRepetions = 0
            beforeLowerPrice = -1
            currentUrl =self.driver.current_url
            #################################################
            ## here it begins to scroll down to get new items
            #################################################
            print "Empezando el scrolling..."
            while True:
                if count==iterations or numOfRepetions==10:
                    break
                print "Scrolling down..."
                try:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1.4)
                    body = self.driver.page_source
                    while True:
                        '''
                        times is the list of items that are shown when you scroll down
                        each item shows the name of person who requests the item, time ago, name of the item, etc
                        there is a screenshot of this, check later
                        '''
                        times = Selector(text=body).xpath("//div[@class='gc12 MD_gc8 LG_gc9']/div[not(@class)]/div")
                        numberOfTimes = len(times) #number of items
                        if numberOfTimes>0:
                            break

                    print "Cantidad de items leidos en la anterior iteracion: " + str(numberOfTimesBefore)
                    print "Cantidad de items leidos en la actual iteracion: " + str(numberOfTimes)
                    if  numberOfTimes==numberOfTimesBefore :
                        print "Sigue siendo la misma cantidad de elementos, entonces no se cargaron bien los items"
                        numOfRepetions= numOfRepetions+1
                    else:
                        numOfRepetions=0
                        count=count+1
                    numberOfTimesBefore=numberOfTimes
                except Exception as e:
                    print str(e)
                    count=count+1
                    pass

            print count
            print numberOfTimes
            print diff
            print limitElements
            sleep(2)
            #elements is also the list of items that you see after you scroll down
            elements = Selector(text=body).xpath("//a[@class='LG_public-inquiry-card--detailed mt10 MD_mt20 public-inquiry-card fx-c fz14 bgc-w bdw1 bdys-s bdc-g12 trd300ms trp-bgc SM_fz-m SM_bdr5 SM_bds-s MD_bgc-g3-hf']")
            links = Selector(text=body).xpath("//a[@class='LG_public-inquiry-card--detailed mt10 MD_mt20 public-inquiry-card fx-c fz14 bgc-w bdw1 bdys-s bdc-g12 trd300ms trp-bgc SM_fz-m SM_bdr5 SM_bds-s MD_bgc-g3-hf']/@href").extract()
            print len(elements)
            if len (elements) == 0:
                print "No ha podido leer elementos"
                sleep(2)
                continue

            #here it begins to check each element(item)
            for i in range(len(elements)):
                offerLink = ""
                precioOferta=None
                hayStanley=False
                isStanley = False
                isFunko = False
                isLol = False
                youMustEdit=False
                print "====================INICIO===================="
                print "**********************************************"
                print "Total: " +str(i+1)+" de "+str(len(elements))
                print "Ofertas procesadas con exito: " + str(completedOffers) #-->va
                print "Ofertas Stanley:" + str(stanleyOffers)
                print "Ofertas Funko Pop:" + str(funkoOffers)
                print "Ofertas L.O.L.:" + str(lolOffers)
                print "Ofertas editadas para mejorar la subasta: " + str(editedOffers) #-->va
                print "Ofertas no creadas por fallar la carga de datos en la web:" + str(failedOffers) #-->va
                print "Ofertas no editadas por fallar la obtencion de su link: " + str(noEditFailedOffers) #-->va
                print "Ofertas no editadas por tener ya, el mejor precio en la subasta: " + str(noEditBetterPrice) #-->va
                print "Ofertas no editadas por fallo para abrir su formulario de edicion: "+ str(noEditUpdateForm)
                print "Ofertas no editada por estar en el tope de la oferta minima (5$) :" + str(noEditLowerPrice) #-->va
                print "Ofertas no editada por haber hecho oferta bajo el criterio squad :" + str(noEditSquadOffer) #-->nueva
                print "Ofertas no editada por ser producto marca Stanley:" + str(noEditStanleyItem) #-->nueva
                print "Ofertas no editada por ser producto marca Funko Pop:" + str(noEditFunkoItem) #-->nueva
                print "Ofertas no editada por ser producto marca LOL:" + str(noEditLolItem) #-->nueva
                print "Ofertas sin ofertantes: " + str(zeroOffers) #-->va
                print "Ofertas potencialmente actualizables pero sin actualizar por no contar con autorizacion (ofertas descartadas): " + str(noEditByNoAuthorization) #-->nueva
                print "Ofertas no existentes: " + str(failedNotExistAnymoreOffers) #-->va
                print "**********************************************"
                ###################################################################################################
                # Flags importantes isTravelSquad, updatingAccepted
                opener = urllib2.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0')]

                elem = elements[i] #en elem tenemos la info del elemento que aparece en la lista de la pagina

                my_item = ScrapyProjectItem()
                nombreUsuarioComprador= elem.xpath(".//div[@class='fx-r ai-c my20 miw0']/div[@class='public-inquiry-card__user d-fx fxd-c fxg1 ai-fs miw0 c-g44']/div[@class='mr5 c-b ellipsis']/text()").extract()
                nombreUsuarioComprador
                nombreItem=elem.xpath(".//div[@class='fxg1 fx-r mb20']/div[@class='fxg1 fx-c miw0']/div[@class='fxg1 fx-r']/div[@class='fxg1 fx-c jc-sb miw0 mx20 SM_mah190']/div[@class='public-inquiry-card__grab-title ov-h fw-sb wow-bw SM_fz-l LG_fz-xl']/text()").extract()
                timeAgoList= elem.xpath("//div[@class='ml5']//text()").extract()

                my_item['nombreUsuarioComprador'] = nombreUsuarioComprador[0]
                my_item['nombreItem'] = nombreItem[0]
                my_item['timeAgo']= timeAgoList[i]
                nombreItem =  nombreItem[0].lower() #pasamos a minuscula el nombre del producto, aunque no recuerdo con que intencion era esto
                tuOferta= elem.xpath(".//span[@class='fw-sb lh-h SM_fz-xxxl']/text()").extract_first()

                print "El nombre del item es: "+ nombreItem.encode('utf-8')
                print tuOferta
                #se obtiene una lista en donde debe ser una lista de un elemento con la oferta que se ha hecho, esta oferta está sin recargos
                link = basepath + links[i] #Obtenemos el link para ver el detalle de la oferta y sacar información adicional
                link = link.encode('utf-8') #link de detalle de oferta
                print "Link de donde sacaremos la info de la oferta: " + link
                #####################
                #tuOferta determina si el camino va por la creacion o actualizacion de la oferta
                #Sacaremos el contenido del detalle de la oferta siempre
                k=0
                ###########################
                #obtener el contenido html del detalle de la oferta para manipular su data sin necesidad de abrir el link
                ###########################
                while(True):
                    try:
                        while not self.internet_on():
                            continue
                        response = opener.open(link,timeout=100)
                        print "Abrio el link"
                        print link
                        html = response.read()
                        response.close()
                        print "Extrajo lectura"
                        break
                    except Exception as e:
                        print str(e)
                        print "No se encontro o fallo en abrir el enlace: " +link
                        print "Seguiremos intentando..."
                        if k==10:   break
                        k=k+1

                if k==10:
                    failedNotExistAnymoreOffers = failedNotExistAnymoreOffers +1
                    message = "El link de detalle de la oferta ya no esta disponible"
                    print "Vamos a pasar y no importa guardar este url porque si no existe no habra ni para oferta, es una oferta que ya dejo de existir"
                    continue
                #################################################################################
                #obtendremos informacion general de la oferta
                names = Selector(text=html).xpath("//section[@class='d-n MD_d-b']/div[@class='w100p bdys-s bdw1 bgc-w SM_bdxs-s SM_bdr5 px20 pt20 bdc-g12 mt20 bdw1 bdc-g12 bdys-s SM_bdxs-s']/div[@class='fx-r ai-c jc-sb SM_bdtr5 pb20']//a[@class='fw-sb ellipsis mr5']/text()").extract()
                print "Names:"
                print names
                prices = Selector(text=html).xpath("//section[@class='d-n MD_d-b']//div[@class='fx-r jc-sb py20 fz14 SM_jc-fs']/span[not(@class)]/text()").extract()
                no_offers = Selector(text=html).xpath("//div[@class='p20 mt20 w100p bgc-w bdw1 bdc-g12 bds-s bdr5 ta-c c-g44']//span//span").extract()
                
                print "Prices:"
                print prices
                priceBaseItem =  Selector(text=html).xpath("//div[@class='c-g44']/span/span/span/text()").extract_first()
                try:
                    precio_base = float(re.search(r'\d+', (priceBaseItem.replace('.','')).replace(',','.') ).group())
                    print "Precio base leido sin errores"
                except:
                    print "No se pudo leer el precio base, continuamos con el siguiente item"
                    print "====================FINAL===================="
                    continue
                precio_tax = 0.0
                try:
                    salesTaxItem =  Selector(text=html).xpath("//div[@class='c-g44']/span/span/span/text()").extract()[1]
                    precio_tax = float(re.search(r'\d+', (salesTaxItem.replace('.','')).replace(',','.') ).group())
                except:
                    print "No hay monto de sales tax para este producto, se dejara como 0"

                numberOfElements= len(names)
                print "Numero de ofertas para el item: "+ str (numberOfElements)
                sublist = {}
                for i in range (0, numberOfElements):
                    sublistItem = {'name':names[i],'price':prices[i]}
                    print sublistItem
                    sublist[i] = sublistItem
                print sublist
                my_item['sublist'] = sublist
                my_item['precioBaseItem'] = priceBaseItem

                #obtendremos el precio minimo y de no ser asi sabremos que AUN NO HAY OFERTAS
                zeroOffersFlag=False
                precioMin = Selector(text=html).xpath("//div[@class='pt5']/a/div/span/span/span/text()").extract_first()
                if precioMin:
                    precioMin = float(re.search(r'\d+', (precioMin.replace('.','')).replace(',','.') ).group())
                    print precioMin
                else:
                    zeroOffersFlag=True
                    zeroOffers = zeroOffers+1
                    message = "No hay ofertas realizadas"
                    ################ aqui tenemos que hallar el precio base + sales tax
                    ### ya se hallaron antes de entrar aqui, ahora toca asignar el valor a precio min
                    precioMin = (precio_base + precio_tax)
                #######################

                #evaluaremos si hay ofertas de travel squad siempre y cuando hayan ofertas
                thereIsSquadOffer= False
                if isTravelSquad and not zeroOffersFlag: #Solo si he autorizado revisar si hay ofertas de squad
                    # TODO check whether variables used within this if are used somewhere else
                    names =  [ sublist[elem]['name'] for elem in sublist ]
                    for i , name in enumerate(names):
                        name = name.lower()
                        if name.find("travel squad") > 0:
                            print "Se encontro una oferta de travel squad asi que replicaremos su oferta, puede haber mas de una iteracion"
                            thereIsSquadOffer = True

                updateException=False
                failException=False
                youMustEdit = False
                youMustPass = False
                #--------------------------------------------------*************-------------------------------------
                print "EMPIEZA LA EVALUACION EN CASO DE QUE SE CREE LA OFERTA(nueva o no) O SE VAYA A QUERER ACTUALIZAR"
                print tuOferta
                if not tuOferta:
                    tuOferta=0

                if tuOferta==0:
                    #no se encuentra la oferta así que no se ha mandado una oferta para este elemento, debemos crear una oferta
                    if zeroOffersFlag:
                        print "No habian ofertas, se creara la primera oferta"
                    else:
                        print "No tienes la etiqueta tu oferta, asi que se debe crear una oferta"
                    if self.isStanley(nombreItem):
                        #caso es un producto stanley
                        print "Se encontro un producto Stanley"
                        isStanley = True
                        quantity = Selector(text=html).xpath("//div[@class='ml20']/text()").extract_first()
                        quantity = int(quantity) if quantity else 1
                        precioOferta = quantity * 25 #coloco el valor predefinido por ser stanley
                        message ="Es un producto de marca Stanley"
                    elif self.isFunko(nombreItem):
                        #caso es un producto funko pop
                        print "Se encontro un producto Funko Pop"
                        isFunko = True
                        quantity = Selector(text=html).xpath("//div[@class='ml20']/text()").extract_first()
                        quantity = int(quantity) if quantity else 1
                        precioOferta = quantity * 15 #valor predefinido por ser funko pop
                        message ="Es un producto de marca Funko Pop"
                    elif self.isLol(nombreItem):
                        #caso es un producto LOL #TODO
                        print "Se encontro un producto LOL"
                        isLol = True
                        quantity = Selector(text=html).xpath("//div[@class='ml20']/text()").extract_first()
                        quantity = int(quantity) if quantity else 1
                        precioOferta = quantity * 20 #valor predefinido por ser LOL
                        message ="Es un producto de marca LOL"
                    else:
                        print "Seguira el flujo normal"
                        if zeroOffersFlag:
                            precioOferta = (precio_base + precio_tax) * 0.20
                            precioOferta = math.ceil(precioOferta)
                            if precioOferta < 10:
                                precioOferta = 10
                            print "Es la primera oferta con precioOferta de {}".format(precioOferta)
                            message ="Es la primera oferta"
                        else:
                            precioOferta = self.getOfferPrice(precioMin)
                            print "Es una nueva oferta con precioOferta de {}".format(precioOferta)
                            message ="Es una nueva oferta"

                    offerButton = Selector(text=html).xpath("//a[@class='btn btn--bb h50 w100p mt20 bdr5 MD_ord4']/@href").extract_first()
                    #se obtiene el enlace para mandar una nueva oferta
                    print offerButton
                    if offerButton :
                        offerLink = basepath + offerButton  #'/grabs/741187/offers/new'
                    else:
                        print "No se pudo obtener el link para poder ofertar"
                        message = "No se pudo obtener el link para poder ofertar"
                        fail
                elif updatingAccepted:
                    print "Se encontro que ya se hizo una oferta asi que puede que este elemento va a nacesitar actualizacion"
                    if self.isStanley(nombreItem):
                        print "Potencial actualizacion pero el producto es Stanley"
                        noEditStanleyItem = noEditStanleyItem +1
                        message = "Oferta no editada por haber ya enviado una oferta y ser Stanley"
                        updateException = True
                    elif self.isFunko(nombreItem):
                        print "Potencial actualizacion pero el producto es Funko Pop"
                        noEditFunkoItem = noEditFunkoItem +1
                        message = "Oferta no editada por haber ya enviado una oferta y ser Funko Pop"
                        updateException = True
                    elif self.isLol(nombreItem):
                        print "Potencial actualizacion pero el producto es LOL"
                        noEditLolItem = noEditLolItem +1
                        message = "Oferta no editada por haber ya enviado una oferta y ser LOL"
                        updateException = True
                    else: #caso normal
                        print "Seguiremos probando si es factible actualizar por el flujo normal"
                        tuOferta = float(re.search(r'\d+', (tuOferta.replace('.','')).replace(',','.')).group())
                        if tuOferta == 5:
                            noEditLowerPrice= noEditLowerPrice +1
                            updateException = True
                        else:
                            print "Tu oferta convertida a flotante: " + str(tuOferta)
                            #abriremos el link un rato para sacar el link de editar
                            print "Link de donde sacaremos la info: "+ link
                            while not self.internet_on():
                                continue

                            self.driver.execute_script('window.open("' + link + '", "_blank");')
                            sleep(2.5)
                            self.driver.switch_to_window(self.driver.window_handles[1])
                            sleep(2)
                            print "Obteniendo el link de editar"
                            WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, "//a[@class='btn btn--g pos-r fxg1 h50 bdr5 mb20 SM_mr10 SM_mb0']")))
                            editButtons =self.driver.find_elements_by_xpath("//a[@class='btn btn--g pos-r fxg1 h50 bdr5 mb20 SM_mr10 SM_mb0']")
                            editLinkExtracted = True
                            if len(editButtons) > 0:
                                editButton = editButtons[0]
                                try:
                                    editLink = editButton.get_attribute("href") #ward solved
                                    print "Se pudo obtener el link de editar..."
                                    print editLink
                                except Exception as e:
                                    print str(e)
                                    editLinkExtracted = False

                            if len(editButtons) == 0 or not editLinkExtracted:
                                print "No se encontro el link para editar"
                                print "Mensaje de excepcion: " + str(e)
                                print "Nos olvidamos de esta oferta y seguimos adelante"
                                noEditFailedOffers = noEditFailedOffers + 1
                                updateException = True
                                message = "Actualizacion fallada porque no se pudo obtener el link de editar"
                            self.driver.close()
                            sleep(1)
                            while not self.internet_on():
                                continue
                            self.driver.switch_to_window(self.driver.window_handles[0])

                            if not updateException:
                                oldOfferValue = tuOferta
                                #abrira el formulario de editar para obtener su valor de la antigua oferta
                                print oldOfferValue
                                if oldOfferValue > precioMin:
                                    if precioMin>=210:
                                        precioOferta = precioMin - 10
                                    elif precioMin >= 105:
                                        precioOferta = precioMin - 5
                                    elif precioMin >= 32:
                                        precioOferta = precioMin - 2
                                    else:
                                        precioOferta = precioMin - 1
                                    precioOferta = math.ceil(precioOferta)
                                    message ="Se va actualizar la oferta"
                                    youMustEdit = True
                                else:
                                    noEditBetterPrice = noEditBetterPrice +1
                                    updateException = True
                                    message = "Actualizacion no puede proceder porque tu oferta es la mejor"
                                if not updateException:
                                    youMustEdit = True

                elif not updatingAccepted and tuOferta!=0:
                    youMustPass = True

                #TERMINA LA EVALUACION DE SI ES PARA CREAR O ACTUALIZAR LA OFERTA
                #--------------------------------------------------*************-------------------------------------
                if youMustPass:
                    noEditByNoAuthorization = noEditByNoAuthorization+1
                    continue

                elif zeroOffersFlag :
                    print "si no hay ofertantes guardamos los datos en el archivo"
                    print my_item
                    tag1 = my_item['nombreUsuarioComprador']
                    tag2 = my_item['nombreItem']
                    print type(my_item['precioBaseItem'])
                    tag3 = my_item['precioBaseItem']
                    print tag3
                    tag4 = link
                    tag1 = tag1.encode('utf-8')
                    tag2 = tag2.encode('utf-8')
                    tag3 = tag3.encode('utf-8') if tag3 is not None else 'None'
                    tag4 = tag4.encode('utf-8')

                    row = tag1+ "," +  tag2 + "," + tag3 + "," + tag4+"\n"
                    csv.write(row)
                    my_item['offerPrice']=-1
                    my_item['message'] = message
                else:
                    if youMustEdit:
                        print "se va a actualizar"
                        while not self.internet_on():
                            continue
                        self.driver.execute_script('window.open("' + editLink + '", "_blank");')
                        sleep(2.5)
                        while not self.internet_on():
                            continue
                        self.driver.switch_to_window(self.driver.window_handles[1])
                        try:
                            while not self.internet_on():
                                continue
                            WebDriverWait(self.driver, 25).until(EC.presence_of_element_located((By.XPATH, "//input[@class='w100p']")))
                            inputOfferElement = self.driver.find_element_by_xpath("//input[@class='w100p']")
                        except Exception as e:
                            print "No se encontro el formulario para editar"
                            print "Mensaje de excepcion: " + str(e)
                            #closing starts
                            self.driver.close()
                            sleep(0.5)
                            while not self.internet_on():
                                continue
                            print "close 2"
                            self.driver.switch_to_window(self.driver.window_handles[0])
                            #closing ends
                            print "Nos olvidamos de esta oferta y seguimos adelante"
                            updateException=True
                            message= "Actualizacion fallada porque no se puedo abrir el formulario de editar"
                            noEditUpdateForm = noEditUpdateForm + 1
                        if not failException:   #si no se generaron excepciones continuamos
                            while not self.internet_on():
                                continue

                            try:
                                inputOfferElement.clear()
                            except Exception as e:
                                print str(e)
                                self.driver.close()
                                sleep(0.5)
                                while not self.internet_on():
                                    continue
                                print "close 2"
                                self.driver.switch_to_window(self.driver.window_handles[0])
                                noEditUpdateForm = noEditUpdateForm+1
                                continue

                            #colocamos el nuevo precio
                            precioOferta = str(int(round(precioOferta)))
                            print precioOferta
                            inputOfferElement.send_keys(precioOferta)
                            editButton  = self.driver.find_element_by_xpath("//button[@class='button pos-r d-ib va-t btn btn--bb w100p h50 px50 mt30 bdr5']")
                            editButton.click()
                            sleep(2)
                            self.driver.close()
                            while not self.internet_on():
                                continue
                            sleep(0.5)
                            self.driver.switch_to_window(self.driver.window_handles[0]) #ward solved
                        my_item['offerPrice']= oldOfferValue
                        my_item['message'] = message
                    elif failException :
                        print "Excepcion por falla"
                        failedOffers = failedOffers +1
                        my_item['offerPrice'] = -1
                        tag1 = my_item['nombreUsuarioComprador']
                        tag2 = my_item['nombreItem']
                        tag1 = tag1.encode('utf-8')
                        tag2 = tag2.encode('utf-8')
                        row = tag1+ "," +  tag2 + "," + link+"\n"
                        csvFailed.write(row)
                    elif updateException:
                        "print Excepcion de edicion por falla"
                        my_item['offerPrice'] = tuOferta
                        tag1 = my_item['nombreUsuarioComprador']
                        tag2 = my_item['nombreItem']
                        tag1 = tag1.encode('utf-8')
                        tag2 = tag2.encode('utf-8')
                        row = tag1+ "," +  tag2 + "," + link+"\n"
                        csvFailed.write(row)
                    if youMustEdit or failException or updateException:
                        yield my_item
                        print "====================FINAL===================="
                        continue #Fin de flujo
                if zeroOffersFlag:
                    print "Vamos a crear la PRIMERA OFERTA"
                else:
                    print "Vamos a crear una NUEVA OFERTA"
                print "El precio de oferta a colocar es: "+ str(precioOferta)
                my_item['offerPrice']= precioOferta
                offerLink = offerLink.encode('utf-8')
                if zeroOffersFlag:
                    print "Vamos a generar la primera oferta en: " + offerLink
                else:
                    print "Vamos a generar una nueva oferta en: " + offerLink
                while not self.internet_on():
                    continue
                self.driver.execute_script('window.open("' + offerLink + '", "_blank");')
                sleep(2)
                self.driver.switch_to_window(self.driver.window_handles[1])

                try:
                    siguienteElement = self.driver.find_element_by_xpath("//div[@class='button__content']/span/span[text()='Siguiente']")
                    sleep(1.5)
                    print "encontro el boton de siguiente"
                    print siguienteElement
                    sleep(2)
                    k=0
                    while True:
                        try:
                            while not self.internet_on():
                                continue
                            addTravelButton  = self.driver.find_element_by_xpath("//div[@class='fx-r jc-sb ai-c']")
                            break
                        except Exception as e:
                            k=k+1
                            if k==5: break
                            sleep(1)
                            print "Pasa por la excepcion 5"
                    if k==5:
                        self.driver.close()
                        while not self.internet_on():
                            continue
                        sleep(0.5)
                        print "Close 4"
                        self.driver.switch_to_window(self.driver.window_handles[0])
                        print "Nos olvidamos de esta oferta y seguimos adelante"
                        failedOffers = failedOffers + 1
                        tag1 = my_item['nombreUsuarioComprador']
                        tag2 = my_item['nombreItem']
                        tag1 = tag1.encode('utf-8')
                        tag2 = tag2.encode('utf-8')
                        row2 = tag1+ "," +  tag2 + "," +  link+"\n"
                        csvFailed.write(row2)
                        my_item['message'] = "Envio de oferta fallida"
                        yield my_item
                        print "====================FINAL===================="
                        continue #Fin de flujo
                    addTravelButton.click()
                    sleep(2)
                    k=0
                    while True:
                        try:
                            beforeTravels=self.driver.find_elements_by_xpath("//label[@class='fx-r px20 py15 z2 trp-bgc cur-p SM_py20 bdts-s bdtc-g12 bdtw1']/span")
                            print "Cantidad de elementos de beforeTravels: " + str(len(beforeTravels))
                            break
                        except Exception as e:
                            k=k+1
                            if k==5: break
                            sleep(1)
                            print "Pasa por la excepcion 6"

                    if k==5:
                        self.driver.close()
                        while not self.internet_on():
                            continue
                        sleep(0.5)
                        print "Close 5"
                        self.driver.switch_to_window(self.driver.window_handles[0])
                        sleep(1.5)
                        print "Nos olvidamos de esta oferta y seguimos adelante"
                        failedOffers = failedOffers +1
                        tag1 = my_item['nombreUsuarioComprador']
                        tag2 = my_item['nombreItem']
                        tag1 = tag1.encode('utf-8')
                        tag2 = tag2.encode('utf-8')
                        row2 = tag1+ "," +  tag2 + "," +  link+"\n"
                        csvFailed.write(row2)
                        my_item['message'] = "Envio de oferta fallida"
                        yield my_item
                        print "====================FINAL===================="
                        continue #Fin de flujo

                    ##########################
                    ##########################
                    today = datetime.now()#fecha actual
                    deltaDays = timedelta(days=1)
                    tomorrow = today + deltaDays
                    tomorrowYear= tomorrow.year
                    print tomorrowYear
                    j=0
                    alreadyDate=False
                    fail=False
                    for j,travel in enumerate(beforeTravels):
                        travelText = travel.text
                        travelText =  travelText.encode('utf-8')
                        posList= [pos for pos, char in enumerate(travelText) if char == ',']
                        if len(posList)<=0:
                            fail=True
                            break

                        posKey= posList[-1]
                        travelText= travelText[posKey+1:len(travelText)]
                        try:
                            print"Travel text"+ travelText
                            listDayMonth = travelText.split(" ")
                            print listDayMonth
                            dayText = int(listDayMonth[1])
                            monthText = (listDayMonth[2]).lower()
                        except Exception as e:
                            print "Se leyeron mal algunos de los viajes anteriores"
                            print "Excepcion: " + str(e)
                            self.driver.close()
                            while not self.internet_on():
                                continue
                            sleep(0.5)
                            print "close 6"
                            self.driver.switch_to_window(self.driver.window_handles[0])
                            print "Nos olvidamos de esta oferta y seguimos adelante"
                            failedOffers = failedOffers +1
                            tag1 = my_item['nombreUsuarioComprador']
                            tag2 = my_item['nombreItem']
                            tag1 = tag1.encode('utf-8')
                            tag2 = tag2.encode('utf-8')
                            row2 = tag1+ "," +  tag2 + "," +  link+"\n"
                            csvFailed.write(row2)
                            my_item['message'] = "Envio de oferta fallida"
                            yield my_item
                            print "====================FINAL===================="
                            continue #Fin de flujo

                        monthText = self.monthStringAbrPoninToInt(monthText)
                        travelDateCurr = datetime(tomorrowYear,monthText,dayText)
                        deltaDays = timedelta(days=1)
                        travelDateCurr = travelDateCurr+deltaDays
                        travelDateFormat = datetime.strptime(travelDate, '%d/%m/%Y')
                        if travelDateCurr == travelDateFormat:
                            print "Ya se habia configurado el viaje..."
                            alreadyDate=True
                            break

                    if fail:
                        print "Fallo la oferta, continuamos con la siguiente"
                        failedOffers= failedOffers +1
                        tag1 = my_item['nombreUsuarioComprador']
                        tag2 = my_item['nombreItem']
                        tag1 = tag1.encode('utf-8')
                        tag2 = tag2.encode('utf-8')
                        row2 = tag1+ "," +  tag2 + "," +  offerLink+"\n"
                        csvFailed.write(row2)
                        my_item['message'] = "Envio de oferta fallida"
                        yield my_item
                        print "====================FINAL===================="
                        continue #Fin de flujo
                    if alreadyDate:
                        travelCurr =beforeTravels[j]
                        travelCurr.click()
                        sleep(1.8)
                    else:
                        print "No tenia una fecha de viaje asi que elegiremos una"
                        print travelDate
                        listDate = travelDate.split("/")
                        dayNumber=int(listDate[0])
                        monthNumber=int(listDate[1])
                        yearNumber =int(listDate[2])

                        inputFromElement = self.driver.find_element_by_xpath("//label[@class='fx-r ai-c cur-d pl15 input input--g mb20 bdr5']//input[@class='fxg1 miw0']")
                        inputFromElement.send_keys(fromCityName)
                        sleep(2)

                        k=0
                        while True:
                            print "Entro a poner la ciudad from"
                            try:
                                fromCitiesList = self.driver.find_elements_by_xpath("//div[@class='link link--b lh1 px20 py15 cur-p ellipsis c-b trd300ms MD_bgc-g3-hf px20 py10 ws-nw ellipsis']")
                                firstCityFrom =  fromCitiesList[fromCityOption-1]
                                firstCityFrom.click()
                                break
                            except Exception as e:
                                k=k+1
                                if k==5: break
                                sleep(1)
                                print "Pasa por la excepcion 7"
                        if k==5:
                            self.driver.close()
                            while not self.internet_on():
                                continue
                            sleep(0.5)
                            print "Close 7"
                            self.driver.switch_to_window(self.driver.window_handles[0])
                            print "Nos olvidamos de esta oferta y seguimos adelante"
                            failedOffers = failedOffers +1
                            tag1 = my_item['nombreUsuarioComprador']
                            tag2 = my_item['nombreItem']
                            tag1 = tag1.encode('utf-8')
                            tag2 = tag2.encode('utf-8')
                            row2 = tag1+ "," +  tag2 + "," +  link+"\n"
                            csvFailed.write(row2)
                            my_item['message'] = "Envio de oferta fallida"
                            yield my_item
                            print "====================FINAL===================="
                            continue #Fin de flujo

                        print "Salio de poner la ciudad from"
                        sleep(1.8)
                        k=0
                        while True:
                            print "Entro para abrir el input de la fecha"
                            try:
                                dateInput = self.driver.find_element_by_xpath("//div[@class='input-substitute fx-r ai-c jc-sb cur-p']")
                                dateInput.click()
                                break
                            except Exception as e:
                                k=k+1
                                if k==5: break
                                sleep(1)
                                print "Pasa por la excepcion 8"
                        if k==5:
                            self.driver.close()
                            while not self.internet_on():
                                continue
                            sleep(0.5)
                            print "Close 8"
                            self.driver.switch_to_window(self.driver.window_handles[0])
                            print "Nos olvidamos de esta oferta y seguimos adelante"
                            tag1 = my_item['nombreUsuarioComprador']
                            tag2 = my_item['nombreItem']
                            tag1 = tag1.encode('utf-8')
                            tag2 = tag2.encode('utf-8')
                            row2 = tag1+ "," +  tag2 + "," +  link+"\n"
                            csvFailed.write(row2)
                            failedOffers = failedOffers +1
                            my_item['message'] = "Envio de oferta fallida"
                            yield my_item
                            print "====================FINAL===================="
                            continue #Fin de flujo

                        print "Salio para abrir el input de la fecha"
                        sleep(1.8)
                        firstTimeFlag= False
                        while True:
                            print "Entro para buscar en el calendario"
                            sleep(1)
                            while not self.internet_on():
                                continue
                            html = self.driver.page_source
                            html= html.encode('utf-8')
                            titleMonthYear = Selector(text=html).xpath("//span[@class='tt-c']/text()").extract()
                            titleMonthYear = titleMonthYear[0]
                            listTitleMonthYear = titleMonthYear.split(" De ")
                            if len(listTitleMonthYear)!=2:
                                listTitleMonthYear = titleMonthYear.split(" de ")

                            monthTitle = (listTitleMonthYear[0]).lower()
                            yearTitleNumber = int(listTitleMonthYear[1])
                            monthTitleNumber = self.monthStringToInt(monthTitle)
                            if(monthTitleNumber == monthNumber and yearTitleNumber == yearNumber):
                                calendarDays = self.driver.find_elements_by_xpath('//div[@class="d-tbcl h35 w35 bds-s bdw1 bdc-g12"]')
                                index=0

                                for calendarDay in calendarDays:
                                    currentDay = calendarDay.text
                                    currentDay = int(currentDay)
                                    if currentDay == dayNumber:
                                        print "Encontro la fecha"
                                        break
                                    index = index+1
                                cday = calendarDays[index]
                                cday.click()
                                print "Termino el ciclo for"
                                break
                            elif (yearNumber*100+monthNumber ) < (yearTitleNumber*100+monthTitleNumber):
                                arrows = self.driver.find_elements_by_xpath("//button[@class='button pos-r d-ib va-t fxs0 fx-r ai-c jc-c p10 bds-s bdw1 bdr-c lh1 c-g44 bdc-g12 cur-p trd300ms MD_c-bb-hf MD_bdc-bb-hf']/div[@class='button__content']")
                                arrowPrev =  arrows[0]
                                arrowPrev.click()
                            else:
                                #print "vamos a mover las flechas para buscar la fecha"
                                arrows = self.driver.find_elements_by_xpath("//button[@class='button pos-r d-ib va-t fxs0 fx-r ai-c jc-c p10 bds-s bdw1 bdr-c lh1 c-g44 bdc-g12 cur-p trd300ms MD_c-bb-hf MD_bdc-bb-hf']/div[@class='button__content']")
                                arrowNext = arrows[1]
                                try:
                                    arrowNext.click()
                                except:
                                    arrowNext = arrows[0]

                                    arrowNext.click()
                                firstTimeFlag=True
                    m=0
                    while True:
                        try:
                            siguienteElement.click()
                            break
                        except Exception as e:
                            m = m+1
                            if m==5:
                                break
                            print "No se pudo dar click en el boton siguiente asi que lo tratamos de reparar"
                            siguienteElement = self.driver.find_element_by_xpath("//div[@class='button__content']/span/span[text()='Siguiente']")

                    sleep(1.8)
                    result=self.makeOffer( my_item , annotation , finalDate , fromCityName , fromCityOption , travelDate ,True )
                    if result== -1:
                        self.driver.close()
                        while not self.internet_on():
                            continue
                        sleep(0.5)
                        print "Close 19"
                        self.driver.switch_to_window(self.driver.window_handles[0])
                        print "NO SALIO BIEN"
                        offerLink = offerLink.encode('utf-8')
                        #guardamos el link en el excel de ofertas fallidas
                        tag1 = my_item['nombreUsuarioComprador']
                        tag2 = my_item['nombreItem']
                        tag1 = tag1.encode('utf-8')
                        tag2 = tag2.encode('utf-8')
                        row2 = tag1+ "," +  tag2 + "," +  link+"\n"
                        csvFailed.write(row2)

                        failedOffers = failedOffers +1
                        my_item['message'] = "Envio de oferta fallida"
                        yield my_item
                        print "====================FINAL===================="
                        continue #Fin de flujo
                    elif result == 1:
                        print "SALIO BIEN"
                        completedOffers =  completedOffers + 1
                        if isStanley:
                            stanleyOffers += 1
                            row = link.encode('utf-8') + "\n"
                            csvStanleys.write(row)
                        elif isFunko:
                            funkoOffers += 1
                            row = link.encode('utf-8') + "\n"
                            csvFunkos.write(row)
                        elif isLol:
                            lolOffers += 1
                            row = link.encode('utf-8') + "\n"
                            csvLols.write(row)
                        yield my_item
                        print "====================FINAL===================="
                except NoSuchElementException :
                    result = self.makeOffer(my_item,annotation,finalDate, fromCityName,fromCityOption,travelDate,False)
                    if result == -1:
                        print "NO SALIO BIEN"
                        self.driver.close()
                        while not self.internet_on():
                            continue
                        sleep(0.5)
                        print "close 20"
                        self.driver.switch_to_window(self.driver.window_handles[0])
                        offerLink = offerLink.encode('utf-8')
                        #guardamos el link en el excel de ofertas fallidas
                        nombreUsuarioComprador = my_item['nombreUsuarioComprador']
                        nombreItem = my_item['nombreItem']
                        nombreUsuarioComprador = nombreUsuarioComprador.encode('utf-8')
                        nombreItem = nombreItem.encode('utf-8')
                        row2 = nombreUsuarioComprador+ "," +  nombreItem + "," +  link+"\n"
                        csvFailed.write(row2)
                        failedOffers = failedOffers +1
                        tag1 = my_item['nombreUsuarioComprador']
                        tag2 = my_item['nombreItem']
                        tag1 = tag1.encode('utf-8')
                        tag2 = tag2.encode('utf-8')
                        row2 = tag1+ "," +  tag2 + "," +  link+"\n"
                        csvFailed.write(row2)
                        my_item['message'] = "Envio de oferta fallida"
                        yield my_item
                        print "====================FINAL===================="
                        continue #Fin de flujo
                    elif result == 1:
                        print "SALIO BIEN"
                        completedOffers =  completedOffers + 1
                        if isStanley:
                            stanleyOffers += 1
                            row = link.encode('utf-8') + "\n"
                            csvStanleys.write(row)
                        elif isFunko:
                            funkoOffers += 1
                            row = link.encode('utf-8') + "\n"
                            csvFunkos.write(row)
                        elif isLol:
                            lolOffers += 1
                            row = link.encode('utf-8') + "\n"
                            csvLols.write(row)
                        yield my_item
                        print "====================FINAL===================="

                self.driver.close()
                while not self.internet_on():
                    continue
                sleep(0.5)

                self.driver.switch_to_window(self.driver.window_handles[0])
                sleep(1.2)

            csv.close()
            csvFailed.close()
            csvStanleys.close()
            csvFunkos.close()
            csvLols.close()
            print "Total: " +str(i+1)+" de "+str(len(elements))
            print "Ofertas procesadas con exito: " + str(completedOffers) #-->va
            print "Ofertas Stanley:" + str(stanleyOffers)
            print "Ofertas Funko Pop:" + str(funkoOffers)
            print "Ofertas L.O.L.:" + str(lolOffers)
            print "Ofertas editadas para mejorar la subasta: " + str(editedOffers) #-->va
            print "Ofertas no creadas por fallar la carga de datos en la web:" + str(failedOffers) #-->va
            print "Ofertas no editadas por fallar la obtencion de su link: " + str(noEditFailedOffers) #-->va
            print "Ofertas no editadas por tener ya, el mejor precio en la subasta: " + str(noEditBetterPrice) #-->va
            print "Ofertas no editadas por fallo para abrir su formulario de edicion: "+ str(noEditUpdateForm)
            print "Ofertas no editada por estar en el tope de la oferta minima (5$) :" + str(noEditLowerPrice) #-->va
            print "Ofertas no editada por haber hecho oferta bajo el criterio squad :" + str(noEditSquadOffer) #-->nueva
            print "Ofertas no editada por ser producto marca Stanley :" + str(noEditStanleyItem) #-->nueva
            print "Ofertas no editada por ser producto marca Funko Pop:" + str(noEditFunkoItem) #-->nueva
            print "Ofertas no editada por ser producto marca LOL:" + str(noEditLolItem) #-->nueva
            print "Ofertas sin ofertantes: " + str(zeroOffers) #-->va
            print "Ofertas actualizables pero sin actualizar por no contar con autorizacion: " + str(noEditByNoAuthorization) #-->nueva
            print "Ofertas no existentes: " + str(failedNotExistAnymoreOffers) #-->va
            print "**********************************************"
            # print "================REPOSO===================="

            if TEST_RUN_FLAG:
                print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
                print "Se ha ejecutado solo un scroll por ser modo de prueba"
                print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
                break

            while not self.internet_on():
                continue
            self.driver.get(currentUrl)
            sleep(6)
        #raise CloseSpider

    def makeDate(self, finalDate, dateMin=None):
        r = re.compile('.{2}/.{2}/.{4}')
        if len(finalDate) == 10:
            if r.match(finalDate):
                if dateMin != None:
                    end_date = datetime.strptime(dateMin, '%d/%m/%Y') + timedelta(days=1)
                    if not (datetime.strptime(finalDate, '%d/%m/%Y') >= end_date):
                        return -1

                listDate = finalDate.split("/")
                dayNumber=int(listDate[0])
                monthNumber=int(listDate[1])
                yearNumber =int(listDate[2])
                try:
                    datetime(yearNumber, monthNumber, dayNumber)
                except Exception as e:
                    print "Ingresa una fecha existente"
                    return 0

                today = datetime.now() + timedelta(days=1)
                dayToday =  today.day
                monthToday =  today.month
                yearToday =  today.year

                if(self.getDateNumber(dayNumber, monthNumber,yearNumber) >= self.getDateNumber(dayToday, monthToday,yearToday)):
                    return finalDate
                else:
                    print "Ingresa una fecha valida"
                    return 0
            else:
                print "Ingresa una fecha con el formato indicado"
                return 0
        else:
            print "Ingresa una fecha con el formato indicado"
            return 0

    def enterDate(self, customMessage, dateMin=None):
        finalDate = raw_input(customMessage)
        r = re.compile('.{2}/.{2}/.{4}')
        if len(finalDate) == 10:
            if r.match(finalDate):

                if dateMin != None:
                    end_date = datetime.strptime(dateMin, '%d/%m/%Y') + timedelta(days=1)
                    if not (datetime.strptime(finalDate, '%d/%m/%Y') >= end_date):
                        return -1

                listDate = finalDate.split("/")
                dayNumber=int(listDate[0])
                monthNumber=int(listDate[1])
                yearNumber =int(listDate[2])

                try:
                    datetime(yearNumber, monthNumber, dayNumber)
                except Exception as e:
                    print "Ingresa una fecha existente"
                    return 0

                today = datetime.now() + timedelta(days=1)
                dayToday =  today.day
                monthToday =  today.month
                yearToday =  today.year

                if(self.getDateNumber(dayNumber, monthNumber,yearNumber) >= self.getDateNumber(dayToday, monthToday,yearToday)):
                    return finalDate
                else:
                    print "Ingresa una fecha valida"
                    return 0

            else:
                print "Ingresa una fecha con el formato indicado"
                return 0
        else:
            print "Ingresa una fecha con el formato indicado"
            return 0

    def getDateNumber(self,day,month,year):
        return year*10000 + month*100 + day

    def makeOffer(self, item,annotation,finaldate, fromCityName,fromCityOption,travelDate, hayFechaViaje=True):
        #finaldate  ya es una fecha verificada
        fail=False
        if not hayFechaViaje:
            #Hemos entrado de frente al segundo paso, para asegurarnos nuestra correcta fecha de viaje
            #regresamos al paso 1 para seleccionarla si es que no existe, o si existe, igual la seleccionamos porciacaso
            print "Vamos a retroceder al primer paso"

            #sleep critico
            sleep(3)
            try:
                print "Empezamos con el riesgo..."
                WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@class='fz14 ta-c mx-a trd1000ms trp-c pt10 px10 c-bb']")))
                print "Por aca siempre hay riesgo de que falle la oferta porque no se encuentra el boton del primer paso"
                firstStep =self.driver.find_element_by_xpath("//div[@class='fz14 ta-c mx-a trd1000ms trp-c pt10 px10 c-bb']")
                print firstStep

                firstStep.click()
                sleep(3)

            except Exception as e:
                print "No se encontro el boton para ir al primer paso"
                print "Mensaje de excepcion: " + str(e)
                print "Nos olvidamos de esta oferta y seguimos adelante"
                return -1

            try:
                print "WARNING: POR AQUI GENERALMENTE OCURRE UNA EXCEPCION QUE HACE FALLAR EL FLUJO DE LA OFERTA"
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='fx-r jc-sb ai-c']")))
                print "Testing 1"
                addTravelButton  = self.driver.find_element_by_xpath("//div[@class='fx-r jc-sb ai-c']")
                print "Testing 2"
                addTravelButton.click()
                print "Testing 3"

            except Exception as e:
                print "No encontramos el boton para agregar viajes"
                print "Mensaje de excepcion: " + str(e)
                print "pasa por la excepcion 2"
                print "nos olvidamos de esta oferta y seguimos adelante"
                return -1

            sleep(1.2)
            k=0
            while True:
                try:
                    beforeTravels=self.driver.find_elements_by_xpath("//label[@class='fx-r px20 py15 z2 trp-bgc cur-p SM_py20 bdts-s bdtc-g12 bdtw1']/span")
                    print "Cantidad de elementos de beforeTravels: " + str(len(beforeTravels))
                    if len(beforeTravels)==0:
                        k=k+1
                        continue

                    break
                except Exception as e:
                    k=k+1
                    if k==5: break
                    sleep(1)
                    print "pasa por la excepcion 3"
            if k==5:
                print "nos olvidamos de esta oferta y seguimos adelante"
                return -1

            print beforeTravels
            print len(beforeTravels)
            today = datetime.now()#fecha actual
            deltaDays = timedelta(days=1)
            tomorrow = today + deltaDays
            tomorrowYear= tomorrow.year
            print tomorrowYear
            j=0
            alreadyDate=False
            for j,travel in enumerate(beforeTravels):
                travelText = travel.text
                print "El texto de viaje dice: " + travelText.encode('utf-8')

                posList= [pos for pos, char in enumerate(travelText) if char == ',']
                if len(posList)<=0:
                    return -1
                print "posList"
                print posList
                posKey= posList[-1]
                travelText= travelText[posKey+1:len(travelText)]

                try:
                    print"Travel text"+ travelText
                    listDayMonth = travelText.split(" ")
                    print listDayMonth
                    dayText = int(listDayMonth[1])
                    monthText = (listDayMonth[2]).lower()
                except Exception as e:
                    print "Se leyeron mas alguno de los viajes anteriores"
                    print "Excepcion:" + str(e)
                    print "Nos olvidamos de esta oferta y seguimos adelante"
                    return -1

                monthText = self.monthStringAbrPoninToInt(monthText)

                print "============================"
                print tomorrowYear
                print monthText
                print dayText
                print "============================"
                travelDateCurr = datetime(tomorrowYear,monthText,dayText)
                deltaDays = timedelta(days=1)
                travelDateCurr = travelDateCurr+deltaDays
                travelDateFormat = datetime.strptime(travelDate, '%d/%m/%Y')
                if travelDateCurr == travelDateFormat:
                    print "Ya se habia configurado el viaje..."
                    alreadyDate=True
                    break

            siguienteElement = self.driver.find_element_by_xpath("//div[@class='button__content']/span/span[text()='Siguiente']")

            if alreadyDate:
                travelCurr =beforeTravels[j]

                travelCurr.click()
                sleep(1.1)
            else:
                listDate = travelDate.split("/")
                dayNumber=int(listDate[0])
                monthNumber=int(listDate[1])
                yearNumber =int(listDate[2])

                inputFromElement = self.driver.find_element_by_xpath("//label[@class='fx-r ai-c cur-d pl15 input input--g mb20 bdr5']//input[@class='fxg1 miw0']")
                while not self.internet_on():
                    continue
                inputFromElement.send_keys(fromCityName)
                WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@class='link link--b lh1 px20 py15 cur-p ellipsis c-b trd300ms MD_bgc-g3-hf px20 py10 ws-nw ellipsis']")))
                fromCitiesList = self.driver.find_elements_by_xpath("//div[@class='link link--b lh1 px20 py15 cur-p ellipsis c-b trd300ms MD_bgc-g3-hf px20 py10 ws-nw ellipsis']")
                print "Logitud de la lista: "+ str(len(fromCitiesList))

                firstCityFrom =  fromCitiesList[fromCityOption-1] #ward solved
                firstCityFrom.click()
                sleep(1.1)

                k=0
                while True:
                    try:
                        dateInput = self.driver.find_element_by_xpath("//div[@class='input-substitute fx-r ai-c jc-sb cur-p']")
                        break
                    except Exception as e:
                        k=k+1
                        if k==5: break
                        sleep(0.5)
                        print "pasa por la excepcion 4"
                if k==5:
                    print "nos olvidamos de esta oferta y seguimos adelante"
                    return -1

                dateInput.click()
                sleep(1)

                firstTimeFlag= False
                while True:
                    sleep(0.5)
                    while not self.internet_on():
                        continue
                    html = self.driver.page_source
                    html= html.encode('utf-8')
                    titleMonthYear = Selector(text=html).xpath("//span[@class='tt-c']/text()").extract()
                    titleMonthYear = titleMonthYear[0]
                    #titleMonthYear = self.driver.find_element_by_xpath("//span[@class='tt-c']").text()
                    print titleMonthYear
                    #titleMonthYear = titleMonthYear[0]
                    listTitleMonthYear = titleMonthYear.split(" De ")
                    if len(listTitleMonthYear)!=2:
                        listTitleMonthYear = titleMonthYear.split(" de ")

                    print listTitleMonthYear
                    monthTitle = (listTitleMonthYear[0]).lower()
                    yearTitleNumber = int(listTitleMonthYear[1])
                    monthTitleNumber = self.monthStringToInt(monthTitle)

                    if(monthTitleNumber == monthNumber and yearTitleNumber == yearNumber):
                        print "Nos quedamos en la pantalla para buscar la fecha"
                        calendarDays = self.driver.find_elements_by_xpath('//div[@class="d-tbcl h35 w35 bds-s bdw1 bdc-g12"]')
                        index=0

                        for calendarDay in calendarDays:
                            print "Index: "+str(index)

                            #pararint "Entro en el for para buscar la fecha"
                            currentDay = calendarDay.text
                            print "Valor:" +currentDay
                            print "vamos a escribir el numero obtenido, puede ser una lista"
                            print "paso la parte complicada"
                            currentDay = int(currentDay)
                            if currentDay == dayNumber:
                                #print "encontro la fecha"
                                break
                            index = index+1
                        cday = calendarDays[index]
                        cday.click()
                        break
                    else:
                        #print "vamos a mover las flechas para buscar la fecha"
                        arrows = self.driver.find_elements_by_xpath("//button[@class='button pos-r d-ib va-t fxs0 fx-r ai-c jc-c p10 bds-s bdw1 bdr-c lh1 c-g44 bdc-g12 cur-p trd300ms MD_c-bb-hf MD_bdc-bb-hf']/div[@class='button__content']")
                        arrowNext = arrows[1]
                        #sleep(3)
                        try:
                            arrowNext.click()
                        except:
                            arrowNext = arrows[0]
                            arrowNext.click()

                        firstTimeFlag=True
            siguienteElement.click()
            sleep(1.5)

        else:
            print "No tuvimos que ir al primer paso"

        listDate = finaldate.split("/")
        dayNumber=int(listDate[0])
        monthNumber=int(listDate[1])
        yearNumber =int(listDate[2])
        print "Estamos en el segundo paso..."
        inputOfferElement=None
        try:
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//input[@type='number']")))
            inputOfferElement =self.driver.find_element_by_xpath("//input[@type='number']")
            sleep(0.2)
            inputOfferElement.clear()

        except Exception as e:
            print "No se ubico el input para el precio"
            print "Mensaje de excepcion: " + str(e)
            print "Nos olvidamos de esta oferta y seguimos adelante"
            return -1

        inputOfferElement.clear()
        inputOfferElement.send_keys(str(int(round(item['offerPrice']))))
        inputDate = self.driver.find_elements_by_xpath("//div[@class='input-substitute fx-r ai-c jc-sb cur-p']")
        inputDate =  inputDate[0]
        inputDate.click()
        firstTimeFlag= False
        while True:
            sleep(0.8)
            while not self.internet_on():
                continue

            while True:
                try:
                    html = self.driver.page_source
                    break
                except httplib.IncompleteRead:
                    continue
                except Exception as e:
                    print "Fallo el self.drive.page_source"
                    print "Mensaje de excepcion: " + str(e)
                    self.driver.close()
                    while not self.internet_on():
                        continue
                    sleep(0.5)
                    print "close 18"
                    self.driver.switch_to_window(self.driver.window_handles[0])
                    print "Nos olvidamos de esta oferta y seguimos adelante"
                    fail = True
                    break
            if fail==True:
                break
            html= html.encode('utf-8')
            titleMonthYear = []
            k=0
            while True:
                try:
                    titleMonthYear = Selector(text=html).xpath("//span[@class='tt-c']/text()").extract()
                    break
                except:
                    k=k+1
                    if k==5:
                        break
            if k==5:
                print "Nos olvidamos de esta oferta y seguimos adelante"
                return -1

            print titleMonthYear
            titleMonthYear = titleMonthYear[0]
            #titleMonthYear = self.driver.find_element_by_xpath("//span[@class='tt-c']").text()
            print titleMonthYear
            #titleMonthYear = titleMonthYear[0]
            listTitleMonthYear = titleMonthYear.split(" De ")
            if len(listTitleMonthYear)!=2:
                listTitleMonthYear = titleMonthYear.split(" de ")

            print "Titulo del calendario"
            print listTitleMonthYear
            monthTitle = (listTitleMonthYear[0]).lower()
            yearTitleNumber = int(listTitleMonthYear[1])
            monthTitleNumber = self.monthStringToInt(monthTitle)
            print "Mes # del calendario :" + str(monthTitleNumber)
            print "Mes objetivo :" + str(monthNumber)
            print "Anho del calendario :" + str(yearTitleNumber)
            print "Anho objetivo :" + str(yearNumber)

            if (monthTitleNumber == monthNumber and yearTitleNumber == yearNumber):
                print "Nos quedamos en la pantalla para buscar la fecha"
                sleep(0.8)
                calendarDays = self.driver.find_elements_by_xpath('//div[@class="d-tbcl h35 w35 bds-s bdw1 bdc-g12"]')
                print calendarDays
                index=0

                for calendarDay in calendarDays:
                    #sleep(1)
                    #print "Index: "+str(index)
                    print "Entro en el for para buscar la fecha"
                    currentDay = calendarDay.text
                    print "Valor:" + currentDay
                    currentDay = int(currentDay)
                    if currentDay == dayNumber:
                        print "encontro la fecha"
                        break
                    index = index+1
                cday = calendarDays[index]
                cday.click()
                print "termino el ciclo for"
                break
            elif(yearNumber*100+monthNumber ) < (yearTitleNumber*100+monthTitleNumber):
                arrows = self.driver.find_elements_by_xpath("//button[@class='button pos-r d-ib va-t fxs0 fx-r ai-c jc-c p10 bds-s bdw1 bdr-c lh1 c-g44 bdc-g12 cur-p trd300ms MD_c-bb-hf MD_bdc-bb-hf']/div[@class='button__content']")
                arrowPrev =  arrows[0]
                arrowPrev.click()
            else:
                #print "vamos a mover las flechas para buscar la fecha"
                arrows = self.driver.find_elements_by_xpath("//button[@class='button pos-r d-ib va-t fxs0 fx-r ai-c jc-c p10 bds-s bdw1 bdr-c lh1 c-g44 bdc-g12 cur-p trd300ms MD_c-bb-hf MD_bdc-bb-hf']/div[@class='button__content']")
                arrowNext = arrows[1]
                #sleep(0.5)
                try:
                    arrowNext.click()
                except:
                    arrowNext = arrows[0]
                    arrowNext.click()

                firstTimeFlag=True
        if fail==True:
            return -1

        print "Aqui empieza la demora"
        inputText = None
        try:
            print "Obtenemos control sobre el area de comentarios"
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//textarea[@class='pos-a t0 l0 h100p w100p rz-n p-i']")))
            inputText = firstStep =self.driver.find_element_by_xpath("//textarea[@class='pos-a t0 l0 h100p w100p rz-n p-i']")
            sleep(1)
            inputText.clear()
            print "Limpiamos el area de comentarios"
        except Exception as e:
            print "No se ubico el textarea"
            print "Mensaje de excepcion: " + str(e)
            print "Nos olvidamos de esta oferta y seguimos adelante"
            return -1

        while not self.internet_on():
            continue

        inputText.click()
        count=0
        while True:
            try:
                print "Intentamos copiar al portapeles la anotacion..."
                copied=pyperclip.copy(annotation)
                break
            except Exception as e:
                count= count +1
                print str(e)
                if count == 20 :
                    print "Closed by pyperclip error"
                    return -1

        inputText.click()
        inputText.send_keys(Keys.CONTROL + "v")
        sleep(1)

        checkboxElement = self.driver.find_element_by_xpath("//div[@class='as-fs fxs0 w20 h20 fx-r ai-c jc-c bdw1 bds-s bdr5 bdc-g44']")
        checkboxElement.click()
        sleep(1)
        print "Vamos a ubicar el boton de mandar oferta"
        try:
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//button[@class='button pos-r d-ib va-t btn btn--bb h50 mt20 px50 w100p bdr5 MD_mt40']")))
            offerButton = self.driver.find_element_by_xpath("//button[@class='button pos-r d-ib va-t btn btn--bb h50 mt20 px50 w100p bdr5 MD_mt40']")

            #sleep critico
            sleep(1)
            offerButton.send_keys(Keys.ENTER)
            sleep(1)
        except Exception as e:
            print "No se ubico el boton para enviar oferta"
            print "Mensaje de excepcion: " + str(e)
            print "Nos olvidamos de esta oferta y seguimos adelante"
            return -1

        print "Vamos a intentar cerrar el pop up dando clic en 'Ahora no'"
        sleep(3)
        try:
            finalPopUp = self.driver.find_element_by_xpath('//div[@class="px20 bgc-g3 pt20"]/div[@class="py15"]')
            print "PopUp captado sin problemas"
        except NoSuchElementException:
            print "No habia pop up"

        try:
            finalPopUp.click()
            print "popUp cerrardo"
        except Exception as e:
            print "No se pudo clickear el final pop up aunque se encontro"

        sleep(2)
        return 1

    def is_valid_email(self,email):
        if len(email) > 7:
            return bool(re.match(
             "^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", email))

    def parse_two (self,response):
        item = response.meta['item']
        names = response.xpath("//section[@class='MD_d-n']//div[@class='fw-sb ellipsis mr5']/text()").extract()
        prices = response.xpath("//section[@class='MD_d-n']//div[@class='fw-sb']/span/text()").extract()
        numberOfNames= len(names)
        numberOfPrices = len(prices)
        numberOfElements= max([ numberOfNames,numberOfPrices])
        sublist = {}
        for i in range (0, numberOfElements):
            sublistItem = {'name':names[i],'price':prices[i]}
            sublist[i] = sublistItem
        item['sublist'] = sublist
        yield item

    def monthStringToInt(self,monthTitle):
        months = {
            "enero":1,
            "febrero":2,
            "marzo":3,
            "abril":4,
            "mayo":5,
            "junio":6,
            "julio":7,
            "agosto":8,
            "setiembre":9,
            "septiembre":9,
            "octubre":10,
            "noviembre":11,
            "diciembre":12
        }
        return months.get(monthTitle, "Invalid month")

    def monthStringAbrPoninToInt(self,monthTitle):
        months = {
            "ene.":1,
            "feb.":2,
            "mar.":3,
            "abr.":4,
            "may.":5,
            "jun.":6,
            "jul.":7,
            "ago.":8,
            "set.":9,
            "sep.":9,
            "oct.":10,
            "nov.":11,
            "dic.":12
        }
        return months.get(monthTitle, "Invalid month")

    def monthNameToSpanish(self,monthEnglishName):
        months = {
            "january": "enero",
            "february": "febrero",
            "march": "marzo",
            "april": "abril",
            "may": "mayo",
            "june": "junio",
            "july": "julio",
            "august": "agosto",
            "september": "setiembre",
            "october": "octubre",
            "november": "noviembre",
            "december": "diciembre"
        }
        return months.get(monthEnglishName, "Invalid month")

    def internet_on(self):
        try:
            urllib2.urlopen('http://216.58.192.142', timeout=100)
            return True
        except urllib2.URLError as err:
            return False

    def moreItems(self, previous_len):
        while not self.internet_on():
            continue
        body = self.driver.page_source
        new_items = Selector(text=body).xpath("//div[@class='ml5']//text()").extract()
        new_len = len(new_items)
        return new_len if new_len > previous_len else 0
    
    def getOfferPrice(self, precioMin):
        precioOferta = 4
        if precioMin>=210:
            precioOferta = precioMin - 10
        elif precioMin >= 105:
            precioOferta = precioMin - 5
        elif precioMin >= 32:
            precioOferta = precioMin - 2
        else:
            precioOferta = precioMin - 1
        precioOferta = math.ceil(precioOferta)
        return precioOferta if precioOferta>=5 else 5
    
    def isStanley(self, nombreItem):
        if nombreItem.find("stanley") >= 0 or nombreItem.find("Stanley") >= 0:
            return True
        return False
    
    def isFunko(self,nombreItem):
        if nombreItem.find("funko") >= 0 or nombreItem.find("Funko") >= 0:
            return True
        return False
    
    def isLol(self, nombreItem):
        ## if itemName is a string just use regex, otherwise find a library that handles this kind of stuff
        ## i mean we could manually check all the posibilities but that would be retarded
        if nombreItem.find("LOL") >= 0 or nombreItem.find("Lol") >= 0 or nombreItem.find("L.O.L") >= 0 or nombreItem.find("l.o.l") >= 0 or nombreItem.find("L.o.l") >= 0:
            return True #turns out i am retarded
        return False
