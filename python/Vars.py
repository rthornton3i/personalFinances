import pandas as pd
import numpy as np

class Inputs():
    file = 'Inputs.xlsx'

    """BASE"""
    inputSheet = 'Inputs'
    salarySheet = 'Salary'

    """LOANS"""
    loanSheet = 'Loans'

    """ALLOCATIONS"""
    allocationsSheet = 'Allocations'
    earningsSheet = 'Earnings'
    accountsSheet = 'Accounts'

    """EXPENSES"""
    carSheet = 'Car'
    homeSheet = 'Home'
    rentSheet = 'Rent'
    foodSheet = 'Food'
    entertainSheet = 'Entertain'
    personalCareSheet = 'Personal Care'
    healthCareSheet = 'Health Care'
    petSheet = 'Pet'
    holidaySheet = 'Holiday'
    charitySheet = 'Charity'
    educationSheet = 'Education'
    vacationSheet = 'Vacation'
    majorSheet = 'Major'
    randomSheet = 'Random'

def dropnan(vals):
    return vals[~pd.isna(vals)]

def getValue(file,sheet,row,col):
    return pd.read_excel(file,sheet,header=None,skiprows=row-1,usecols=col,nrows=1).iloc[0,0]

class Vars():
    def __init__(self):
        self.base = self.Base()
        self.salary = self.Salary()
        self.filing = self.Filing()
        self.children = self.Children()
        
        self.loans = self.Loans()
        self.expenses = self.Expenses()  
        
        self.benefits = self.Benefits()
        self.taxes = self.Taxes()
        self.savings = self.Savings()
        self.accounts = self.Accounts()

    class Base(Inputs):
        def __init__(self):
            super().__init__()

            inputFields = pd.read_excel(self.file,self.inputSheet,header=None,index_col=0,skiprows=1,usecols='A,C:D',nrows=26,names=None)
            
            self.loops = inputFields.loc['Iterations'].values[0]
            self.years = inputFields.loc['Years'].values[0]

            self.baseAges = inputFields.loc['Ages'].values[0:].astype(int)
            self.retAges  = inputFields.loc['Retirement Age'].values[0:].astype(int)
            
            self.numInd = len(self.baseAges)
    
    class Filing(Inputs):
        def __init__(self):
            super().__init__()

            inputFields = pd.read_excel(self.file,self.inputSheet,header=None,index_col=0,skiprows=1,usecols='A,C',nrows=26,names=None)
            
            self.filingType  = inputFields.loc['Filing'].values[0]
            self.filingState = inputFields.loc['Filing State'].values[0]
    
    class Salary(Inputs):
        def __init__(self):
            super().__init__()

            inputFields = pd.read_excel(self.file,self.inputSheet,header=None,index_col=0,skiprows=1,nrows=26,names=None).drop(columns=1)

            self.salOpt  = dropnan(inputFields.loc['Salary Option'].values[0:])
            self.salBase = dropnan(inputFields.loc['Salary'].values[0:])
            self.prevSal = [dropnan(inputFields.loc['Previous Salary (#1)'].values[0:]),dropnan(inputFields.loc['Previous Salary (#2)'].values[0:])]

            self.salGrowth = inputFields.loc['Salary Growth'].values[0:3]
            self.salBonus  = inputFields.loc['Bonus'].values[0:3]
            self.promotionChance     = inputFields.loc['Chance of Promotion'].values[0]
            self.promotionWaitPeriod = inputFields.loc['Promotion Wait Period'].values[0]
            self.promotionGrowth     = inputFields.loc['Promotion Growth'].values[0:3]

            self.wageInd = inputFields.loc['Inflation Average'].values[0]
            self.wageDev = inputFields.loc['Inflation Std Dev'].values[0]

            self.salCustom = pd.read_excel(self.file,self.salarySheet,header=None,skiprows=1,index_col=0,names=None) if any([opt.upper() == 'CUSTOM' for opt in self.salOpt]) else None
    
    class Children(Inputs):
        def __init__(self):
            super().__init__()

            inputFields = pd.read_excel(self.file,self.inputSheet,header=None,index_col=0,skiprows=1,nrows=26,names=None).drop(columns=1)

            self.childBaseAges     = dropnan(inputFields.loc['Child Ages'].values[0:]).astype(int)
            self.maxChildYr        = inputFields.loc['Max Age of Childcare'].values[0]
            self.childInflationVal = inputFields.loc['Child Inflation'].values[0]

    class Loans(Inputs):
        def __init__(self):
            super().__init__()

            self.loanSummary = pd.read_excel(self.file,self.loanSheet,header=1,usecols='A:D',
                                             names=['loanYr','prin','term','rate']).dropna()

            self.numLoans = self.loanSummary.shape[0]

    class Expenses:
        def __init__(self):
            self.cars = self.Cars()
            self.house = self.House()
            self.rent = self.Rent()
            
            self.food = self.Food()
            self.entertain = self.Entertain()
            self.personalCare = self.PersonalCare()
            self.healthcare = self.Healthcare()
            self.pet = self.Pet()
            
            self.holiday = self.Holiday()
            self.charity = self.Charity()
            
            self.education = self.Education()
            self.vacation = self.Vacation()
            self.major = self.Major()
            self.random = self.Random()
        
        class Cars(Inputs):
            def __init__(self):
                super().__init__()

                self.carSummary = pd.read_excel(self.file,self.carSheet,header=1,usecols='A:G',
                                                names=['purYr','sellYr','prin','down','app','term','rate']).dropna().reset_index(drop=True)
                
                self.allocation = getValue(self.file,self.carSheet,row=7,col='J')

                carFields = pd.read_excel(self.file,self.carSheet,header=None,index_col=0,skiprows=1,usecols='I,K:M',nrows=4,names=None)
                self.insurance  = carFields.loc['Insurance'].values[0]
                self.repairs    = carFields.loc['Repairs'].values[0:]
                self.fuel       = carFields.loc['Fuel'].values[0]
                self.ezpass     = carFields.loc['EZ Pass'].values[0]

                self.numCars = self.carSummary.shape[0]

        class Rent:
            def __init__(self):
                self.rentYr = []
                
                # Total cost per month
                self.baseRent = 2100
                self.rentFees = 75 + 50 + 25 # Parking, Pet, Trash
                
                self.repairs = 50
                self.insurance = 20
                
                self.electricity = 140
                self.gas = 20      
                self.water = 40
            
        class House(Inputs):
            def __init__(self):
                super().__init__()
                
                self.houseSummary = pd.read_excel(self.file,self.homeSheet,header=1,usecols='A:G',
                                            names=['purYr','sellYr','prin','down','app','term','rate']).dropna()
            
                self.allocation = getValue(self.file,self.homeSheet,row=10,col='J')

                homeFields = pd.read_excel(self.file,self.homeSheet,header=None,index_col=0,skiprows=1,usecols='I,K:M',nrows=7,names=None)
                self.propTax        = homeFields.loc['Property Tax'].values[0]
                self.insurance      = homeFields.loc['Insurance'].values[0]
                self.repairs        = homeFields.loc['Repairs'].values[0:]
                self.electricity    = homeFields.loc['Electricity'].values[0]
                self.gas            = homeFields.loc['Gas'].values[0]
                self.water          = homeFields.loc['Water'].values[0]
                self.sewage         = homeFields.loc['Sewage'].values[0]
                        
                self.numHouses = self.houseSummary.shape[0]
            
        class Food(Inputs):
            def __init__(self):
                super().__init__()

                self.allocation = getValue(self.file,self.foodSheet,row=2,col='F')

                foodFields = pd.read_excel(self.file,self.foodSheet,header=None,index_col=0,skiprows=1,usecols='A,C',names=None)
                self.groceries      = foodFields.loc['Groceries'].values[0]
                self.restaurants    = foodFields.loc['Restaurants'].values[0]
                self.otherFood      = np.sum([cost.values[0] if not (foodType == 'Groceries' or foodType == 'Restaurants') else 0 for foodType,cost in foodFields.iterrows()])
        
        class Entertain(Inputs):
            def __init__(self):
                super().__init__()

                self.allocation = getValue(self.file,self.entertainSheet,row=8,col='B')

                entertainFields = pd.read_excel(self.file,self.entertainSheet,header=None,index_col=0,skiprows=1,nrows=5,names=None).drop(columns=1)
                self.internet       = entertainFields.loc['Internet'].values[0]
                self.phone          = entertainFields.loc['Phone'].values[0]
                self.tv             = dropnan(entertainFields.loc['TV'].values[0:])
                self.software       = dropnan(entertainFields.loc['Software'].values[0:])
                self.memberships    = dropnan(entertainFields.loc['Memberships'].values[0:])
            
        class PersonalCare(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation = getValue(self.file,self.personalCareSheet,row=8,col='B')

                personalCareFields = pd.read_excel(self.file,self.personalCareSheet,header=None,index_col=0,skiprows=1,nrows=5,names=None).drop(columns=1)
                self.clothing   = personalCareFields.loc['Clothing'].values[0]
                self.shoes      = personalCareFields.loc['Shoes'].values[0]
                self.hair       = personalCareFields.loc['Hair'].values[0]
                self.makeup     = personalCareFields.loc['Makeup'].values[0]
                self.products   = personalCareFields.loc['Products'].values[0]
        
        class Healthcare(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation = getValue(self.file,self.healthCareSheet,row=12,col='B')

                insuranceFields = pd.read_excel(self.file,self.healthCareSheet,header=None,index_col=0,skiprows=1,nrows=9,names=None).drop(columns=1)
                self.deductible     = dropnan(insuranceFields.loc['Deductible'].values[0:])
                self.coinsurance    = dropnan(insuranceFields.loc['Coinsurance'].values[0:])
                self.maxOOP         = dropnan(insuranceFields.loc['Max Out-of-Pocket'].values[0:])
                
                self.visits = insuranceFields.loc['# of Visits'].values[0:3]
                self.costs  = insuranceFields.loc['Cost per Visit'].values[0:3]
                self.drugs  = insuranceFields.loc['Pharmacy'].values[0]

                self.hsaOpt = insuranceFields.loc['HSA'].values[0]\
            
        class Pet(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation = getValue(self.file,self.petSheet,row=8,col='B')

                petFields = pd.read_excel(self.file,self.petSheet,header=None,index_col=0,skiprows=1,nrows=5,names=None).drop(columns=1)
                self.food       = petFields.loc['Food'].values[0]
                self.essentials = petFields.loc['Essentials'].values[0]
                self.toys       = petFields.loc['Toys'].values[0]
                self.careTaker  = petFields.loc['Caretaker'].values[0]
                self.vet        = petFields.loc['Vet'].values[0]
        
        class Holiday(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation = getValue(self.file,self.holidaySheet,row=13,col='B')

                holidayFields = pd.read_excel(self.file,self.holidaySheet,header=None,index_col=0,skiprows=1,nrows=11,names=None).drop(columns=1)
                self.familyBday = holidayFields.loc['Family Birthday'].values[0]
                self.familyXmas = holidayFields.loc['Family Holidays'].values[0]
                
                self.childBday = holidayFields.loc['Children Birthday'].values[0]
                self.childXmas = holidayFields.loc['Children Holidays'].values[0]
                
                self.persBday   = holidayFields.loc['Personal Birthday'].values[0]
                self.persXmas   = holidayFields.loc['Personal Holidays'].values[0]
                self.persVal    = holidayFields.loc['Personal Valentines'].values[0]
                self.persAnniv  = holidayFields.loc['Personal Anniversary'].values[0]
        
        class Charity(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation = getValue(self.file,self.charitySheet,row=4,col='B')

                charityFields = pd.read_excel(self.file,self.charitySheet,header=None,index_col=0,skiprows=1,nrows=1,names=None).drop(columns=1)
                self.baseChar = charityFields.loc['Donations'].values[0]
        
        class Education(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation = getValue(self.file,self.educationSheet,row=7,col='B')

                educationFields = pd.read_excel(self.file,self.educationSheet,header=None,index_col=0,skiprows=1,nrows=4,names=None).drop(columns=1)
                self.tuition    = educationFields.loc['Tuition'].values[0]
                self.housing    = educationFields.loc['Housing'].values[0]
                self.dining     = educationFields.loc['Dining'].values[0]
                self.books      = educationFields.loc['Books'].values[0]
        
        class Vacation(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation = getValue(self.file,self.vacationSheet,row=10,col='B')

                vacationFields = pd.read_excel(self.file,self.vacationSheet,header=None,index_col=0,skiprows=1,nrows=5,names=None).drop(columns=1)
                self.travel     = vacationFields.loc['Travel'].values[0:3]
                self.hotel      = vacationFields.loc['Hotel'].values[0:3]
                self.food       = vacationFields.loc['Food'].values[0]
                self.events     = vacationFields.loc['Events'].values[0]
                self.carRental  = vacationFields.loc['Rental'].values[0]
                
                self.numDays = pd.read_excel(self.file,self.vacationSheet,header=None,skiprows=7,usecols='C:E',nrows=1).iloc[0].values
        
        class Major(Inputs):
            def __init__(self):
                super().__init__()
                
                self.majorSummary = pd.read_excel(self.file,self.majorSheet,header=1,usecols='A,C',
                                                  names=['purYr','cost']).dropna()
                
                self.allocation = getValue(self.file,self.majorSheet,row=2,col='F')
        
        class Random(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation = getValue(self.file,self.randomSheet,row=6,col='B')

                randomFields = pd.read_excel(self.file,self.randomSheet,header=None,index_col=0,skiprows=1,nrows=3,names=None).drop(columns=1)
                self.maxExp         = randomFields.loc['Max Cost'].values[0]
                self.decayFactor    = randomFields.loc['Decay Factor'].values[0]
                self.binWid         = randomFields.loc['Bin Width'].values[0]                
    
    class Benefits:
        def __init__(self):
            self.health = self.Health()
            self.retirement = self.Retirement()
            self.socialSecurity = self.SocialSecurity()
        
        class Health:
            def __init__(self):
                # Cost per year per individual
                self.hsa = 1500
                self.fsa = 0*12
                self.hra = 0*12    
                
                self.medicalPrem = (148*12)
                self.visionPrem = (14*12)
                self.dentalPrem = (28*12)
                
                self.healthDed = []
                self.healthBen = []
        
        class Retirement:
            def __init__(self):
                self.traditional = self.Args()
                self.roth = self.Args()
                self.match = self.Args()
                
                self.rmdAge = 72
                self.rmdFactor = [0.00962,2.345,144.617]
                
                self.rmdDist = []
                self.netTradCont = []
                self.netRothCont = []
            
                self.maxSelfCont = 22500
                self.maxTotalCont = 66000
                self.maxCatchUpCont = 7500
                self.catchUpAge = 50

                self.traditional.basePerc = 0                
                self.roth.basePerc = 0.1
                
                self.match.maxPerc = 0.06
                self.match.basePerc = 0.04
 
            class Args:
                def __init__(self):
                    self.basePerc = []
                    self.maxPerc = []
                    
                    self.contribution = []
                    self.withdrawal = []
            
        class SocialSecurity(Inputs):
            def __init__(self):
                super().__init__()

                inputFields = pd.read_excel(self.file,self.inputSheet,header=None,index_col=0,skiprows=1,usecols='A,C:D',nrows=26,names=None)

                self.collectionAge = dropnan(inputFields.loc['SS Collection Age'].values[0:])
                
                self.fullRetAge = 67
                self.earlyRetAge = [5/900,5/1200]
                self.lateRetAge = 5/900
                
                # https://www.ssa.gov/oact/cola/AWI.html
                self.wageIndex = 60575.07
                
                self.bendPerc = [0.9,0.32,0.15]
                self.bendPts = [1115,6721,1e9]
                self.bendSlope = [[0.33,25],[1.99,155]]
            
                self.ssIns = []
                self.ssTax = []
        
    class Taxes:
        def __init__(self):
            self.federal = self.Federal()
            self.state = self.State()
            
            self.totalTaxes = []
            self.totalDeducted = []
            self.totalWithheld = []
            self.netIncome = []
            self.netCash = []
            self.totalTradRet = []
            self.totalRothRet = []

        class Federal:
            def __init__(self):
                self.fica = self.Fica()
                self.deductions = self.Deductions()
                self.exemptions = self.Exemptions()
                
                self.grossIncomeFed = []
                self.fedTax = []
                self.ficaTax = []

            class Fica:
                def __init__(self):
                    self.ss = self.SS()
                    self.med = self.MED()

                class SS:
                    def __init__(self):
                        self.ssTax = []

                class MED:
                    def __init__(self):
                        self.medTax = []      

            class Deductions:
                def __init__(self):
                    self.itemized = self.Itemized()
                    self.standard = self.Standard()

                class Itemized:
                    def __init__(self):
                        self.itemDedFed = []

                class Standard:
                    def __init__(self):
                        self.stdDedFed = []
            
            class Exemptions:
                def __init__(self):
                    self.exemptFed = []    

        class State:
            def __init__(self):
                self.local = self.LocalTax()
                self.deductions = self.Deductions()
                self.exemptions = self.Exemptions()
            
                self.grossIncomeState = []
                self.stateTax = []
                self.saltTaxes = []
            
            class LocalTax:
                def __init__(self):
                    self.localTax = []            

            class Deductions:
                def __init__(self):
                    self.itemized = self.Itemized()
                    self.standard = self.Standard()

                class Itemized:
                    def __init__(self):
                        self.itemDedState = []

                class Standard:
                    def __init__(self):
                        self.stdDedState = []
            
            class Exemptions:
                def __init__(self):
                    self.persExempt = self.PersExempt()
                    self.childExempt = self.ChildExempt()
                
                class PersExempt:
                    def __init__(self):
                        self.persExemptState = []
                

                class ChildExempt:
                    def __init__(self):
                        self.childExemptState = []
    
    class Savings():
        def __init__(self):
            self.savings = []
            self.contributions = []
            self.withdrawals = []

            self.allocations = []
            self.earnings = []
            self.expenses = []
    
    class Accounts(Inputs):
        def __init__(self):
            super().__init__()
            
            self.allocations = pd.read_excel(self.file,self.allocationsSheet,skiprows=1,index_col=0,header=None)
            self.earnings = pd.read_excel(self.file,self.earningsSheet,skiprows=2,index_col=0,header=None)
            self.accountSummary = pd.read_excel(self.file,self.accountsSheet,skiprows=2,index_col=0,header=None,names=['baseSavings','capGainsType','accountType'])

                            # To, From, [OPT] Yr
            # self.underflow =   [[[10],[9]],
            #                     [[9],[8]],
            #                     [[8],[4,3,2,1,0]],
            #                     [[7],[4,3,2,1,0]]]
        
            #             # From, To, Max, [OPT] Yr
            # self.overflow =    [[4,3,250e3],
            #                     [4,3,0,15],
            #                     [3,2,2e6],
            #                     [2,1,2e6,25],
            #                     [1,0,2e6,25]]


# al = vars.accounts()
# for att, _ in al.__dict__.items():
#     print(att)
# print('here')


# vars = Vars()
# print('here')