import math
import random
import re
import sys
from time import sleep
from typing import Set, Optional, Dict, List

import inquirer


VRIENDEN: Set[str] = {"NAAM1", "NAAM2", "NAAM3", "NAAM4"}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class LootjesTrekker:
    """
    Lootjestrekker 2.0
    (2.0 is vanwege blockchain-IoT-revolution-support)

    "Voor als je iedereen in je vriendengroep even kut vindt en niemand elkaar vertrouwt."

    Kiest random een subgroep uit een groep vrienden. B.v. om meej die kroma mensen uit te sluiten.
    Eerst wordt gevraagd hoeveel mensen er IN TOTAAL mogen zijn, en wie er sowieso al aanwezig zijn. Daarna kiest
    iedere mattie een geheel getal waarvan het 'zaad' wordt gemaakt (het zaad wordt samengesteld op alfabetische
    volgorde van de namen).

     Voorbeeld met vrienden "Berrie", "Batsbak", en "Tartiflette" bij gastheer "Gastheer":

     Lootjestrekker: "Hoeveel guys mogen er in totaal zijn inclusief jezelf enzo?"

     Gastheer: "3"

     Lootjestrekker: "Wie hebben kkveel white privilege en moeten er sowieso bij zijn?"

     Gastheer: "Gastheer"

     Lootjestrekker: "Voer jullie zaad in".

     Op whatsapp:
        Berrie: "1"
        Batsbak: "123087235378925 ik ben kkgrappig"
        Tartiflette: "23578"

     Het 'zaad' wordt nu de som van de zaadjes = 1 + 123087235378925 + 23578 = 123087235402494

     Gastheer vult in: 123087235378925123578

     Met het zaad wordt een willekeurig-getal-generator gemaakt die altijd dezelfde random uitkomst geeft voor
     hetzelfde zaad, dus dan is het bij onenigheden te verifieren voordat er gevochten wordt.
     (super blockchain verifieerbaar dus jwz).

     Lootjestrekker kiest:
        "Berrie", "Batsbak"

    Tartiflette is de zak.
    """

    def __init__(self):
        self.zaad: Optional[int] = None
        self.vrienden: List[str] = []

        self.antw_dict = {}

        self.n_allowed_total = 0
        self.n_allowed_extra = 0

        self.lootboys: Set[str] = set()
        self.gelukkigen: Set[str] = set()
        self.iedereen: Set[str] = set()

        self._init_vrienden()

    def _init_vrienden(self):
        # Sorteer op alfabetische volgorde
        self.vrienden = [' '.join(v) for v in
                         sorted((vrind.split(' ') for vrind in VRIENDEN), key=lambda x: (x[-1], x[0]))]

    @staticmethod
    def bevestig(msg: str = "Akkoord?") -> bool:
        response = inquirer.prompt(
            [inquirer.List('janeequit', message=msg, choices=['Ja', 'Nee', 'Afsluiten'])])['janeequit']
        if response == 'Ja':
            return True
        elif response == 'Nee':
            return False
        elif response == 'Afsluiten':
            print("Oke doei")
            sys.exit(0)

    def vriend_keuze(self, vraag: str, vrienden: List[str], sep=', ',
                     vraagid: str = 'vriendkeuze', min_: int = 0) -> Dict[str, List[str]]:
        print("Selecteer antwoorden met spatie, druk enter om je selectie te bevestigen.")

        _attempts = 5

        while True:
            antwoord = inquirer.prompt([inquirer.Checkbox(name=vraagid, message=vraag, choices=vrienden)])
            if not antwoord[vraagid] and len(antwoord[vraagid]) < min_:
                print("Meer invullen lul..")
                continue
            print(f"Je keuze bestond uit: {sep.join(antwoord[vraagid]) if antwoord[vraagid] else 'niemand...'}")
            if self.bevestig():
                self.antw_dict.update(antwoord)
                return self.antw_dict
            print("Oke, opnieuw kiezen dan...")

    def loting(self, lootboys: List[str]):
        self.antw_dict['zaadjes'] = []
        maxno = math.floor(9223372036854775807 / len(lootboys))
        zaaddict = inquirer.prompt(
            [inquirer.Text(lootboy,
                           message=f"Welk zaadgetal kiest {lootboy}? (tussen 0 en {maxno})",
                           validate=lambda _, x: re.match(r'^\d+$', x) if 0 <= int(x) <= maxno else False)
             for lootboy in lootboys])

        print(f"Zaadkeuzes: \n")
        for key, val in zaaddict.items():
            print(f"\t{key}: {val}")

        self.zaad = sum(int(zaaddict[lootboy]) for lootboy in lootboys)

        print(f"Het gekozen zaadgetal is de som van de zaadgetallen dus dat wordt {self.zaad}.")

        random.seed(self.zaad)
        self.gelukkigen |= set(random.choices(population=lootboys, k=self.n_allowed_extra))

        print("Lotteray time...")
        granted = f'{bcolors.OKGREEN}GRANTED{bcolors.ENDC}'
        denied = f'{bcolors.FAIL}DENIED{bcolors.ENDC}'
        iedereenshuffled = self.iedereen.copy()
        random.shuffle(list(iedereenshuffled))
        for idx, guy in enumerate(iedereenshuffled):
            chosen = guy in self.gelukkigen

            for i in range(5):
                print(f"{bcolors.BOLD}{bcolors.OKBLUE}{guy}{bcolors.ENDC}{bcolors.BOLD}: ACCESS {'.'*i}{bcolors.ENDC}", end='\r')
                sleep(random.randint(1, 5)*0.25)
            print(
                f"{bcolors.BOLD}{bcolors.OKGREEN if chosen else bcolors.FAIL}{guy}{bcolors.ENDC}: ACCESS {granted if chosen else denied}{bcolors.ENDC}{bcolors.ENDC}")

    @staticmethod
    def hoeveel_mogen_er_zijn() -> int:
        nallowed = int(inquirer.prompt(
            [inquirer.Text(
                name='hoeveel',
                message="Hoeveel mensen mogen er in totaal ZIJN, dus inclusief gastheren enzo?",
                validate=lambda _, x: re.match(r'^\d+$', x) if 1 <= int(x) <= int(100e9) else False)])['hoeveel'])
        print(f"Er mogen {nallowed} mensen komen{'; das echt kneiterveel...' if nallowed > 300 else '.'}")
        if nallowed == 1:
            print("Dat zal een spannende loting worden dan...")
        return nallowed

    def run(self):

        self.n_allowed_total = self.hoeveel_mogen_er_zijn()

        self.vriend_keuze('Wie moeten er sowieso bij zijn en hoeven niet te loten?',
                          self.vrienden, vraagid="gastheren")

        self.n_allowed_extra = self.n_allowed_total - len(self.antw_dict['gastheren'])

        self.gelukkigen |= set(self.antw_dict['gastheren'])
        self.iedereen |= self.gelukkigen

        self.lootboys = [vriend for vriend in self.vrienden if vriend not in self.antw_dict['gastheren']]

        self.antw_dict.update(self.vriend_keuze('Wie willen er allemaal komen?',
                                                self.lootboys, vraagid="gegadigden", min_ = 1))

        self.lootboys = [lootboy for lootboy in self.lootboys if lootboy in self.antw_dict['gegadigden']
                         and lootboy not in self.antw_dict['gastheren']]
        self.iedereen |= set(self.lootboys)

        if len(self.iedereen) <= self.n_allowed_total:
            print("WEJOOO IEDEREEN MAG KOMEN ER HOEFT NIET GELOOT TE WORDEN.")
            sys.exit(0)

        self.loting(self.lootboys)


if __name__ == '__main__':
    lt = LootjesTrekker()
    lt.run()