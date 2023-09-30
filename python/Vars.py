import pandas as pd

class Inputs():
    file = 'Inputs.xlsx'

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

class Vars():
    def __init__(self):
        self.base = self.Base()
        self.salary = self.Salary()
        self.filing = self.Filing()
        self.children = self.Children()
        
        self.expenses = self.Expenses()  
        
        self.benefits = self.Benefits()
        self.taxes = self.Taxes()
        self.savings = self.Savings()
        self.accounts = self.Accounts()
    
    class Base:
        def __init__(self):
            self.loops = 1
            self.years = 60

            self.baseAges = [28,28]
            self.retAges = [55,55]
            self.ages = []
            
            self.numInd = len(self.baseAges)
    
    class Filing:
        def __init__(self):
            self.filingType = "JOINT"
            self.filingState = ["NJ","NJ"]
            
            self.iters = []
    
    class Salary:
        def __init__(self):
            self.salBase   = [96000,119800]
            self.prevSal = [[88428,80354,94175,93107],[98049,99027,114805,109016]]

            self.salGrowth = [0.025,0.035,0.045] #%
            self.salBonus = [0.0,0.04,0.065] #% for each individual
            self.promotionChance = 0.25
            self.promotionWaitPeriod = 3
            self.promotionGrowth = [0.06,0.08,0.125]

            self.wageInd = 0#0.035#0.043
            self.wageDev = 0#0.023
            
            self.salary = []
            self.income = []
            self.grossIncome = []  
            self.inflation = []
    
    class Children:
        def __init__(self):
            self.childYrs = [1,3]
            self.maxChildYr = 22
            self.childInflationVal = 0.35
            
            self.childAges = []
            self.childInflation = []
    
    
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
            
            self.totalExp = []
            self.totalExpenses = []
            
            self.numExpenses = 13
        
        class Cars(Inputs):
            def __init__(self):
                super().__init__()

                self.carSummary = pd.read_excel(self.file,self.carSheet,header=1,usecols='A:G',
                                                names=['purYr','sellYr','prin','down','app','term','rate']).dropna()
                
                self.allocation = pd.read_excel(self.file,self.carSheet,header=None,skiprows=7,usecols='J',nrows=1).iloc[0,0]

                carFields = pd.read_excel(self.file,self.carSheet,header=None,index_col=0,skiprows=1,usecols='I,K:M',nrows=5,names=None)
                self.insurance  = carFields.loc['Insurance'].values[0]
                self.repairs    = carFields.loc['Repairs'].values[0:]
                self.fuel       = carFields.loc['Fuel'].values[0]
                self.ezpass     = carFields.loc['EZ Pass'].values[0]

                self.preBal = carFields.loc['Previous Balance'].values[0]

                self.carBal = []
                self.carPay = []
                self.carPrn = []
                self.carInt = []
                self.carWth = []
                self.carDwn = []
                
                self.total = []

                self.numCars = self.carSummary.shape[0]

        class Rent:
            def __init__(self):
                self.rentYr = [0,1]
                
                # Total cost per month
                self.baseRent = 2100
                self.rentFees = 75 + 50 + 25 # Parking, Pet, Trash
                
                self.repairs = 50
                self.insurance = 20
                
                self.electricity = 140
                self.gas = 20      
                self.water = 40
                
                self.total = []
            
        class House(Inputs):
            def __init__(self):
                super().__init__()
                
                self.houseSummary = pd.read_excel(self.file,self.homeSheet,header=1,usecols='A:G',
                                            names=['purYr','sellYr','prin','down','app','term','rate']).dropna()
            
                self.allocation = pd.read_excel(self.file,self.homeSheet,header=None,skiprows=9,usecols='J',nrows=1).iloc[0,0]

                homeFields = pd.read_excel(self.file,self.homeSheet,header=None,index_col=0,skiprows=1,usecols='I,K:M',nrows=7,names=None)
                self.propTax        = homeFields.loc['Property Tax'].values[0]
                self.insurance      = homeFields.loc['Insurance'].values[0]
                self.repairs        = homeFields.loc['Repairs'].values[0:]
                self.electricity    = homeFields.loc['Electricity'].values[0]
                self.gas            = homeFields.loc['Gas'].values[0]
                self.water          = homeFields.loc['Water'].values[0]

                self.preBal = homeFields.loc['Previous Balance'].values[0]

                self.houseBal = []
                self.housePay = []
                self.housePrn = []
                self.houseInt = []
                self.houseWth = []
                self.houseDwn = []
                
                self.total = []
                        
                self.numHouses = self.houseSummary.shape[0]
            
        class Food(Inputs):
            def __init__(self):
                super().__init__()

                self.allocation = pd.read_excel(self.file,self.foodSheet,header=None,skiprows=7,usecols='B',nrows=1).iloc[0,0]

                foodFields = pd.read_excel(self.file,self.foodSheet,header=None,index_col=0,skiprows=1,usecols='A,C',nrows=5,names=None)
                self.groceries      = foodFields.loc['Groceries'].values[0]
                self.restaurants    = foodFields.loc['Restaurants'].values[0]
                self.alcohol        = foodFields.loc['Alcohol'].values[0]
                self.fastFood       = foodFields.loc['Fast Food'].values[0]
                self.workFood       = foodFields.loc['Work Food'].values[0]
                
                self.total = []
        
        class Entertain(Inputs):
            def __init__(self):
                super().__init__()

                self.allocation = pd.read_excel(self.file,self.entertainSheet,header=None,skiprows=7,usecols='B',nrows=1).iloc[0,0]

                entertainFields = pd.read_excel(self.file,self.entertainSheet,header=None,index_col=0,skiprows=1,nrows=5,names=None).iloc[:,1:]
                self.internet       = entertainFields.loc['Internet'].values[0]
                self.phone          = entertainFields.loc['Phone'].values[0]
                self.tv             = entertainFields.loc['TV'].values[0:]
                self.software       = entertainFields.loc['Software'].values[0:]
                self.memberships    = entertainFields.loc['Memberships'].values[0:]
                
                self.total = []
            
        class PersonalCare(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation = pd.read_excel(self.file,self.personalCareSheet,header=None,skiprows=7,usecols='B',nrows=1).iloc[0,0]

                personalCareFields = pd.read_excel(self.file,self.personalCareSheet,header=None,index_col=0,skiprows=1,nrows=5,names=None).iloc[:,1:]
                self.clothing   = personalCareFields.loc['Clothing'].values[0]
                self.shoes      = personalCareFields.loc['Shoes'].values[0]
                self.hair       = personalCareFields.loc['Hair'].values[0]
                self.makeup     = personalCareFields.loc['Makeup'].values[0]
                self.products   = personalCareFields.loc['Products'].values[0]
                
                self.total = []
        
        class Healthcare(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation = pd.read_excel(self.file,self.healthCareSheet,header=None,skiprows=11,usecols='B',nrows=1).iloc[0,0]

                insuranceFields = pd.read_excel(self.file,self.healthCareSheet,header=None,index_col=0,skiprows=1,nrows=3,names=None).iloc[:,1:]
                self.deductible     = insuranceFields.loc['Deductible'].values[0:]
                self.coinsurance    = insuranceFields.loc['Coinsurance'].values[0:]
                self.maxOOP         = insuranceFields.loc['Max Out-of-Pocket'].values[0:]

                visitFields = pd.read_excel(self.file,self.healthCareSheet,header=None,index_col=0,skiprows=5,nrows=3,names=None).iloc[:,1:]
                self.visits = visitFields.loc['# of Visits'].values[0:]
                self.costs  = visitFields.loc['Cost per Visit'].values[0:]
                self.drugs  = visitFields.loc['Pharmacy'].values[0]

                self.hsaOpt = pd.read_excel(self.file,self.healthCareSheet,header=None,skiprows=9,usecols='C',nrows=1).iloc[0,0]
                
                self.total = []
            
        class Pet(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation = pd.read_excel(self.file,self.petSheet,header=None,skiprows=7,usecols='B',nrows=1).iloc[0,0]

                petFields = pd.read_excel(self.file,self.petSheet,header=None,index_col=0,skiprows=1,nrows=5,names=None).iloc[:,1:]
                self.food       = petFields.loc['Food'].values[0]
                self.essentials = petFields.loc['Essentials'].values[0]
                self.toys       = petFields.loc['Toys'].values[0]
                self.careTaker  = petFields.loc['Caretaker'].values[0]
                self.vet        = petFields.loc['Vet'].values[0]
                
                self.total = []
        
        class Holiday(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation = pd.read_excel(self.file,self.holidaySheet,header=None,skiprows=12,usecols='B',nrows=1).iloc[0,0]

                familyFields = pd.read_excel(self.file,self.holidaySheet,header=None,index_col=0,skiprows=1,nrows=2,names=None).iloc[:,1:]
                self.familyBday = familyFields.loc['Family Birthday'].values[0]
                self.familyXmas = familyFields.loc['Family Holidays'].values[0]
                
                childrenFields = pd.read_excel(self.file,self.holidaySheet,header=None,index_col=0,skiprows=4,nrows=2,names=None).iloc[:,1:]
                self.childBday = childrenFields.loc['Children Birthday'].values[0]
                self.childXmas = childrenFields.loc['Children Holidays'].values[0]
                
                personalFields = pd.read_excel(self.file,self.holidaySheet,header=None,index_col=0,skiprows=7,nrows=4,names=None).iloc[:,1:]
                self.persBday   = personalFields.loc['Personal Birthday'].values[0]
                self.persXmas   = personalFields.loc['Personal Holidays'].values[0]
                self.persVal    = personalFields.loc['Personal Valentines'].values[0]
                self.persAnniv  = personalFields.loc['Personal Anniversary'].values[0]
                
                self.total = []        
        
        class Charity(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation = pd.read_excel(self.file,self.charitySheet,header=None,skiprows=3,usecols='B',nrows=1).iloc[0,0]

                charityFields = pd.read_excel(self.file,self.charitySheet,header=None,index_col=0,skiprows=1,nrows=1,names=None).iloc[:,1:]
                self.baseChar = charityFields.loc['Donations'].values[0]
                
                self.total = []
#         
        
        class Education(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation = pd.read_excel(self.file,self.educationSheet,header=None,skiprows=6,usecols='B',nrows=1).iloc[0,0]

                educationFields = pd.read_excel(self.file,self.educationSheet,header=None,index_col=0,skiprows=1,nrows=4,names=None).iloc[:,1:]
                self.tuition    = educationFields.loc['Tuition'].values[0]
                self.housing    = educationFields.loc['Housing'].values[0]
                self.dining     = educationFields.loc['Dining'].values[0]
                self.books      = educationFields.loc['Books'].values[0]
                
                self.total = []
        
        class Vacation(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation = pd.read_excel(self.file,self.vacationSheet,header=None,skiprows=9,usecols='B',nrows=1).iloc[0,0]

                vacationFields = pd.read_excel(self.file,self.vacationSheet,header=None,index_col=0,skiprows=1,nrows=5,names=None).iloc[:,1:]
                self.travel     = vacationFields.loc['Travel'].values[0]
                self.hotel      = vacationFields.loc['Hotel'].values[0]
                self.food       = vacationFields.loc['Food'].values[0]
                self.events     = vacationFields.loc['Events'].values[0]
                self.carRental  = vacationFields.loc['Rental'].values[0]
                
                self.numDays = pd.read_excel(self.file,self.vacationSheet,header=None,skiprows=7,usecols='C:E',nrows=1).iloc[0].values
                
                self.total = []
        
        class Major(Inputs):
            def __init__(self):
                super().__init__()
                
                self.majorSummary = pd.read_excel(self.file,self.majorSheet,header=1,usecols='A,C',
                                                names=['purYr','cost']).dropna()
                
                self.allocation = pd.read_excel(self.file,self.majorSheet,header=None,skiprows=1,usecols='F',nrows=1).iloc[0,0]

                self.total = []
        
        class Random(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation = pd.read_excel(self.file,self.randomSheet,header=None,skiprows=5,usecols='B',nrows=1).iloc[0,0]

                randomFields = pd.read_excel(self.file,self.randomSheet,header=None,index_col=0,skiprows=1,nrows=3,names=None).iloc[:,1:]
                self.maxExp         = randomFields.loc['Max Cost'].values[0]
                self.decayFactor    = randomFields.loc['Decay Factor'].values[0]
                self.binWid         = randomFields.loc['Bin Width'].values[0]
                
                self.total = []
    
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
            
        class SocialSecurity:
            def __init__(self):
                self.collectionAge = [70,70]
                
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
                    self.localTax =[]            

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