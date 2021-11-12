import mysql
from mysql.connector import connect, Error
from selenium import webdriver
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import config
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

idList = []
linkList = []
errorList = []
errorPattern = ["error_no_fb_url",
                "error_ambassador_fb_company",
                "error_ambassador_fb_position",
                "error_ambassador_fb_company_url",
                "error_ambassador_fb_mfi_url"]
try:
    connection = mysql.connector.connect(host='socratka.mysql.tools',
                                         database='socratka_test20210303mfi',
                                         user='socratka_marchak',
                                         password='66sOZEbo2Vp466sOZEbo2Vp4')
    if connection.is_connected():
        select_ambassadors = "SELECT T1.user_id, T2.meta_value FROM(SELECT * FROM " \
                             "wp_usermeta WHERE " \
                             "meta_key = 'social_facebook') AS T2 RIGHT JOIN (SELECT * FROM (SELECT * FROM " \
                             "wp_usermeta WHERE meta_key = 'wp_capabilities') AS T WHERE " \
                             "meta_value LIKE '%ambassador%') AS T1 ON T1.user_id = T2.user_id "
        with connection.cursor() as cursor:
            cursor.execute(select_ambassadors)
            result = cursor.fetchall()
            for row in result:
                link = str(row)
                link = link.replace("'", "").replace("(", "").replace(")", "").replace(" ", "").split(",")
                print(link)
                idList.append(link[0])
                linkList.append(link[1])


except Error as e:
    print("Error while connecting to MySQL", e)

op = webdriver.ChromeOptions()
op.add_argument('headless')
driver = webdriver.Chrome(executable_path="chromeDriver/chromedriver2", options=op)

driver.get("https://www.facebook.com/")
email = driver.find_element_by_css_selector("input[name='email']")
email.send_keys(config.LOGIN)
password = driver.find_element_by_css_selector("input[name='pass']")
password.send_keys(config.PASSWORD)
inBut = driver.find_element_by_css_selector("button[name='login']")
inBut.click()
# time.sleep(3)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='bp9cbjyn j83agx80 "
                                                                                 "datstx6m taijpn5t oi9244e8']")))
for i, user in enumerate(linkList):
    isFBLink = False
    isWork = False
    isWorkEqual = False
    isWorkLink = False
    isLink = False
    userErrorList = []  # добавил, удалил errorList выше
    if not user == "None":
        isFBLink = True
        driver.get(user)
        # time.sleep(3)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[class='a8c37x1j "
                                                                                         "ni8dbmo4 stjgntxs "
                                                                                         "l9j0dhe7']")))

        try:
            work = driver.find_element_by_xpath("//*[contains(text(), 'Investments.mentorsflow.com')]")
            isWork = True
        except NoSuchElementException as e:
            isWork = False
        # print("isWork %s" % isWork)

        try:
            workEqual = driver.find_element_by_css_selector(
                "span[class='d2edcug0 hpfvmrgz qv66sw1b c1et5uql oi732d6d ik7dh3pa ht8s03o8 "
                "a8c37x1j keod5gw0 nxhoafnm aigsh9s9 d9wwppkn fe6kdd0r mau55g9w c8b282yb "
                "iv3no6db jq4qci2q a3bd9o3v b1v8xokw oo9gr5id hzawbc8m']")

            if workEqual.text.__contains__("Ambassador в Investments.mentorsflow.com") or workEqual.text.__contains__(
                    "Co-Founder/Owner в Investments.mentorsflow.com"):
                isWorkEqual = True
        except NoSuchElementException as e:
            isWorkEqual = False
        # print("isWorkEqual %s" % isWorkEqual)

        if isWork:
            work_a = driver.find_element_by_css_selector("a[class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 "
                                                         "r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 "
                                                         "cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 "
                                                         "a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl oo9gr5id "
                                                         "gpro0wi8 lrazzd5p']").get_attribute("href")

            if work_a == "https://www.facebook.com/investments.mentorsflow/":
                isWorkLink = True

            # print("isWorkLink %s" % isWorkLink)
        try:
            link = driver.find_element_by_xpath("//*[contains(text(), 'investments.mentorsflow.com/')]")
            isLink = True
        except NoSuchElementException as e:
            isLink = False
        # print("isWork %s" % isLink)
    else:
        isFBLink = False

    if not isFBLink:
        print("error_no_fb_url")
        userErrorList.append(1)
    else:
        userErrorList.append(0)

    if not isWork:
        print("error_ambassador_fb_company")
        userErrorList.append(1)
    else:
        userErrorList.append(0)

    if not isWorkEqual:
        print("error_ambassador_fb_position")
        userErrorList.append(1)
    else:
        userErrorList.append(0)

    if not isWorkLink:
        print("error_ambassador_fb_company_url")
        userErrorList.append(1)
    else:
        userErrorList.append(0)

    if not isLink:
        print("error_ambassador_fb_mfi_url")
        userErrorList.append(1)
    else:
        userErrorList.append(0)

    # if isFBLink and isWork and isWorkEqual and isWorkLink and isLink:
    #     print("success_ambassador_fb")
    #     userErrorList.append(1)
    # else:
    #     userErrorList.append(0)
    errorList.append(userErrorList)
driver.close()

try:
    if connection.is_connected():
        select_ambassadors = "DELETE FROM wp_usermeta WHERE meta_key LIKE " \
                             "'%ambassador_verified%' "
        with connection.cursor() as cursor:
            cursor.execute(select_ambassadors)
            connection.commit()

            for i, id in enumerate(idList):
                for j, err in enumerate(errorList[i]):
                    if connection.is_connected():
                        select_ambassadors = "INSERT INTO wp_usermeta(user_id, meta_key, meta_value) " \
                                             "VALUES " \
                                             "(%s, '%s', '%s')" % (idList[i], errorPattern[j], err)

                        with connection.cursor() as cursor:
                            cursor.execute(select_ambassadors)
                            connection.commit()
except Error as e:
    print("Error while connecting to MySQL", e)

if connection.is_connected():
    cursor.close()
    connection.close()
