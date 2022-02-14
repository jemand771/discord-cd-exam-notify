import os

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


import model
from model import MScore


class CDApi:

    def __init__(self, username, password):
        chrome_options = Options()
        if not os.environ.get("NO_HEADLESS"):
            chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_window_size(1920, 1080)
        self.driver.implicitly_wait(5)
        self._do_login(username, password)

    def _do_login(self, username, password):
        self.driver.get("https://selfservice.campus-dual.de/index/login")
        self.driver.find_element(By.ID, "sap-user").send_keys(username)
        self.driver.find_element(By.ID, "sap-password").send_keys(password)
        self.driver.find_element(By.ID, "LOGON_BUTTON").click()

    @property
    def cookie(self):
        while True:
            sess = self.driver.get_cookie("PHPSESSID")
            if sess is not None:
                return sess["value"]

    def get_exam_results(self):
        self.driver.get("https://selfservice.campus-dual.de/acwork/index")
        results = self.driver.find_elements(By.CSS_SELECTOR, "div#mscore a.mscore")
        return [self._make_mscore(x) for x in results]

    @staticmethod
    def _make_mscore(mscore_link):
        table_cols = mscore_link.find_element(By.XPATH, "../../..").find_elements(By.CSS_SELECTOR, "td")
        return MScore(
            module=mscore_link.get_attribute("data-module"),
            year=mscore_link.get_attribute("data-peryr"),
            period=mscore_link.get_attribute("data-perid"),
            date_score=table_cols[4].text,
            date_publish=table_cols[5].text,
        )

    def _result_dist_helper(self, mscore, dist=True):
        return requests.get(
            "https://selfservice.campus-dual.de/acwork/mscore" + "dist" * dist,
            cookies={"PHPSESSID": self.cookie},
            params={
                "peryr": mscore.year,
                "perid": mscore.period,
                "module": mscore.module
            },
            verify=False  # TODO look into why ssl verification fails
        ).json()

    def get_result_dist(self, mscore):

        summary = self._result_dist_helper(mscore, False)
        dist = self._result_dist_helper(mscore, True)
        return model.MScoreDist(
            results=[x["COUNT"] for x in dist],
            texts=[x["GRADETEXT"] for x in dist],
            open=summary[0],
            done=summary[1]
        )
