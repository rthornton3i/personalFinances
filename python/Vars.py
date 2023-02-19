class Vars:
    def __init__(self):
        self.base = self.Base()
        self.salary = self.Salary()
        self.filing = self.Filing()
        self.children = self.Children()
        
        self.expenses = self.Expenses()  
        
        self.benefits = self.Benefits()
        self.taxes = self.Taxes()
        # self.savings = self.Savings()
        # self.allocations = self.Allocations()
    
    class Base:
        def __init__(self):
            self.loops = 1
            self.years = 70

            self.baseAges = [28,28]
            self.retAges = [55,55]
            self.ages = []
            
            self.numInd = len(self.baseAges)

            self.inflation = 0.02
    
    class Filing:
        def __init__(self):
            self.filingType = "JOINT"
            self.filingState = ["NJ","NJ"]
            
            self.iters = []
    
    class Salary:
        def __init__(self):
            self.salBase   = [93000,115200]
            self.prevSal = [[75000,79750,88940,90000],[83000,87720,95000,107500]]

            self.salGrowth = [0.025,0.035,0.045] #%
            self.salBonus = [0.065,0.04] #% for each individual
            self.promotionChance = [2,0.25] # [minYrsBtw,chanceOtherwise]
            self.promotionGrowth = [0.06,0.085,0.125]
            
            self.salary = []
            self.income = []
            self.grossIncome = []  
    
    class Children:
        def __init__(self):
            self.childYrs = [1,3]
            self.maxChildYr = 22
            self.childInflation = 0.3
            
            self.childAges = []
    
    
    class Expenses:
        def __init__(self):
            self.cars = self.Cars()
            self.housing = self.Housing()
            
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
        
        class Cars:
            def __init__(self):
    #                           Rich  , Becca , CO1   , S1    , CO2   , S2    , Ch1   , Ch2   , S3a   , S3b     S4a   , S4b        
                self.purYr  = [-4    , -4    , 5     , 7     , 13    , 16    , 22    , 24    , 21    , 24    , 29    , 32]     
                self.sellYr = [5     , 7     , 13    , 16    , 21    , 24    , -1    , -1    , 29    , 32    , -1    , -1]     
                self.term   = [5     , 5     , 5     , 5     , 5     , 5     , 5     , 5     , 5     , 5     , 5     , 5]
                self.prin   = [23500 , 19500 , 25000 , 25000 , 30000 , 30000 , 22500 , 22500 , 35000 , 35000 , 40000 , 40000]  
                self.down   = [20    , 20    , 20    , 20    , 20    , 20    , 20    , 20    , 20    , 20    , 20    , 20]  
                self.app    = [-20   , -20   , -20   , -20   , -20   , -20   , -20   , -20   , -20   , -20   , -20   , -20]
                self.rate   = [1.9   , 1.9   , 1.9   , 1.9   , 1.9   , 1.9   , 1.9   , 1.9   , 1.9   , 1.9   , 1.9   , 1.9]

                self.preBal = 0
                self.preWth = 0
                
                # Total cost per month
                self.insurance = 100+110
                # Percent of worth (payment**)
                self.repairs = 0.025 #[100,400,2500]
                
                # Additional cost relative to pre-child expense
                self.insRepChildFactor = 0.35

                # Total cost per month
                self.fuel   = 400
                self.ezpass = 300
                
                # Additional cost relative to pre-child expense
                self.fuelEzChildFactor = 0.25

                self.carBal = []
                self.carPay = []
                self.carPrn = []
                self.carInt = []
                self.carWth = []
                self.carDwn = []
                
                self.totalCar = []

                self.numCars = len(self.purYr)

        class Housing:
            def __init__(self):
                self.rent = self.Rent()
                self.house = self.House()

            class Rent:
                def __init__(self):
                    self.rentYr = []
                    
                    # Total cost per month
                    self.baseRent = 2100
                    self.rentFees = 75 + 50 + 25 # Parking, Pet, Trash
                    self.rentInc = 0.05
                    
                    self.repairs = 50
                    self.insurance = 20
                    
                    self.electricity = 140
                    self.gas = 20      
                    self.water = 40
                    
                    self.totalRent = []
                
            class House:
                def __init__(self):
                    self.purYr  = [-1     , 18     , 33]
                    self.sellYr = [18     , 33     , -1]
                    self.term   = [28     , 3      , 15]
                    self.rate   = [2.75   , 4      , 3.25]
                    self.prin   = [562500 , 850000 , 1250000]
                    self.down   = [20     , 20     , 20]
                    self.app    = [1.5    , 2.0    , 2.0]

                    self.preBal = 0
                    self.preWth = 0
                    
                    # Percent of worth
                    self.propTax = 0.017
                    self.repairs  = 0.0125
                    self.insurance = 0.0035
                    
                    # Total cost per month
                    self.electricity = 3.5*30
                    self.gas = 3.2*30          
                    self.water = 50

                    self.houseBal = []
                    self.housePay = []
                    self.housePrn = []
                    self.houseInt = []
                    self.houseWth = []
                    self.houseDwn = []
                    
                    self.totalHouse = []
                            
                    self.numHouses = len(self.purYr)
            
        class Food:
            def __init__(self):
                # Total cost per month
                self.groceries = 650
                self.restaurants = 200
                self.alcohol = 30
                self.fastFood = 30
                self.workFood = 30
                
                # Additional cost relative to pre-child expense
                self.childFactor = 0.4
                # Overall growth after 'years'
                self.growthFactor = 0.2
                
                self.totalFood = []
        
        class Entertain:
            def __init__(self):
                # Total cost per month
                self.wifi = 55
                self.cell = 80
                self.tv   = 0
                self.subs = (130/12) + 65 + (60/12) + (130/12) + (220/12) + (625/12) + (75/12) + (22/12) + (120/12)
                            #Amazon, Youtube, Nest, Costco, Beach, Chase, Microsoft, Nintendo, Dropbox
                
                # Additional cost relative to pre-child expense
                self.childFactor = 0.25
                # Overall growth after 'years'
                self.growthFactor = 0.5
                
                self.totalEnt = []
            
        class PersonalCare:
            def __init__(self):
                # Total cost per month
                self.clothingShoes = 75
                self.hairMakeup = 60
                
                # Additional cost relative to pre-child expense
                self.childFactor = 0.25
                # Overall growth after 'years'
                self.growthFactor = 0.25
                
                self.totalPers = []
        
        class Healthcare:
            def __init__(self):
                # Total cost per month
                self.drugs = [250/12]
                
                # Individual
                self.deductible = [3000]
                self.coinsurance = [0.3]
                self.maxOOP = [9100]
                
                self.hsaOpt = [True]
                
                self.visits = [0,1,3]
                self.costs = [40,200,1500]
                
                # Additional cost relative to pre-child expense
                self.childFactor = 0.25
                # Overall growth after 'years'
                self.growthFactor = 0.25
                
                self.totalHealth = []
            
        class Pet:
            def __init__(self):
                # Total cost per month
                self.food = 75
                self.essentials = 20
                self.toys = 15
                self.careTaker = 0
                self.vet = (100+250)/12
                self.insurance = 30
                        
                # Overall growth after 'years'
                self.growthFactor = 1.5
                
                self.totalPet = []
        
        class Holiday:
            def __init__(self):
                # Overall growth after 'years'
                self.familyGrowthFactor = 0.5
                self.childGrowthFactor = 2
                
                # Cost per year
                self.familyBday = 500
                self.familyXmas = 1000
                
                # Cost per year per child
                self.childBday = 100
                self.childXmas = 300
                
                # Cost per year per person
                self.persBday = 100
                self.persXmas = 200
                self.persVal = 100
                self.persAnniv = 150
                
                self.totalHol = []        
        
        class Charity:
            def __init__(self):
                self.baseChar = 0.01
                
                self.totalChar = []
#         
        
        class Education:
            def __init__(self):
                # Cost per year per child
                self.tuition = 50000
                self.housing = 12000
                self.dining = 3000
                self.books = 1500
                
                self.totalEd = []
        
        class Vacation:
            def __init__(self):
                self.travel = 400 # Cost per person
                
                self.food = 25 + 20 + 40 # Cost per day per person
                self.events = 50 # Cost per day per person
                
                self.hotel = 300 # Cost per day
                self.carRental = 60 # Cost per day
                
                self.numDays = 5
                
                # Overall growth after 'years'
                self.growthFactor = 1
                
                self.totalVac = []
        
        class Major:
            def __init__(self):
                self.wedding =  [[1,55000]]

                self.totalMajor = []
        
        class Random:
            def __init__(self):
                self.maxExp = 50000
                self.decayFactor = 4
                self.binWid = 5
                
                self.totalRand = []
    
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
                self.netTradRet = []
                self.netRothRet = []
            
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
                
                self.fra = 67
                self.fraEarly = [5/900,5/1200]
                self.fraLate = 5/900
                
                self.wageIndex = [2799.16,2973.32,3139.44,3155.64,3301.44,3532.36,3641.72,3673.8,3855.8,4007.12,4086.76,4291.4,4396.64,4576.32,4658.72,4938.36,5213.44,5571.76,5893.76,6186.24,6497.08,7133.8,7580.16,8030.76,8630.92,9226.48,9779.44,10556.03,11479.46,12513.46,13773.1,14531.34,15239.24,16135.07,16822.51,17321.82,18426.51,19334.04,20099.55,21027.98,21811.6,22935.42,23132.67,23753.53,24705.66,25913.9,27426,28861.44,30469.84,32154.82,32921.92,33252.09,34064.95,35648.55,36952.94,38651.41,40405.48,41334.97,40711.61,41673.83,42979.61,44321.67,44888.16,46481.52,48098.63,48642.15,50321.89,52145.8,54099.99,55628.6,60575.07]
                self.wageInd = 0.0325
                self.cola = 0.0138
                
                self.bendPerc = [0.9,0.32,0.15]
                self.bendPts = [996,6002]
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
    
    class Savings:
        def __init__(self):
            self.allocations
            self.earnings
            self.contributions
            self.savings
    
    class Allocations:
        def __init__(self):
            self.accountName = ["HIGH DIVIDEND",
                                "LOW VOLATILITY",
                                "VALUE & GROWTH",
                                "SECTOR & INDEX",
                                "SWING & DAY",
                                "ROTH 401K",
                                "TRADITIONAL 401K",
                                "COLLEGE 529",
                                "LONG-TERM SAVINGS",
                                "SHORT-TERM SAVINGS",
                                "SPENDING"]
        
            self.accountType = ["INVESTING",
                                "INVESTING",
                                "INVESTING",
                                "INVESTING",
                                "INVESTING",
                                "INVESTING",
                                "INVESTING",
                                "INVESTING",
                                "SAVINGS",
                                "SAVINGS",
                                "SAVINGS"]
        
            self.capGainsType = ["LONG",
                                 "LONG",
                                 "LONG",
                                 "LONG",
                                 "SHORT",
                                 "NONE",
                                 "SHORT",
                                 "NONE",
                                 "NONE",
                                 "NONE",
                                 "NONE"]
        
            self.baseSavings = [0.15*29000,             #hiDiv      
                                0.15*29000,             #lowVol   
                                0.10*29000,             #valueGrowth   
                                0.10*29000,             #sectorInd
                                0.50*29000,             #swingDay    (Vanguard-TEMP)
                                9000 + 19500 + 17500,   #retRoth401  (L3Harris, NG, L'Oreal)
                                0,                      #retTrad401 
                                1700,                   #col529      (Fidelity)
                                73000 + 30000,          #longTerm    (Goldman Sach's)
                                1000,                   #shortTerm   (PNC Growth, BoA Savings)
                                5000 + 10000]           #spend       (PNC Spend, BoA Spend)
        
            self.allocations = [[1 , 1 , 2 , 3 , 3],    # 0 - hiDiv
                                [1 , 1 , 2 , 3 , 3],    # 1 - lowVol
                                [1 , 2 , 3 , 1 , 0],    # 2 - valueGrowth
                                [1 , 2 , 2 , 1 , 0],    # 3 - sectorInd
                                [4 , 2 , 1 , 0 , 0],    # 4 - swingDay
                                [0 , 0 , 0 , 0 , 0],    # 5 - retRoth401
                                [0 , 0 , 0 , 0 , 0],    # 6 - retTrad401
                                [3 , 8 , 9 , 0 , 0],    # 7 - col529
                                [5 , 8 , 5 , 3 , 10],   # 8 - longTerm
                                [3 , 5 , 5 , 3 , 3],    # 9 - shortTerm
                                [10, 10, 10, 10, 5]]    # 10 - spend
        
                              # Mean, Std
            self.earnings =    [[4.0,0.5],
                                [8.0,2.5],
                                [10.0,3.0],
                                [10.0,15.0],
                                [30.0,30.0],
                                [10.0,3.0,4.0,1.0],
                                [10.0,3.0,4.0,1.0],
                                [8.0,3.0,5.0,2.0],
                                [1.5,0.5],
                                [0.05,0.01],
                                [0.01,0.01]]
        
                            # To, From, [OPT] Yr
            self.underflow =   [[[10],[9]],
                                [[9],[8]],
                                [[8],[4,3,2,1,0]],
                                [[7],[4,3,2,1,0]]]
        
                        # From, To, Max, [OPT] Yr
            self.overflow =    [[4,3,250e3],
                                [4,3,0,15],
                                [3,2,2e6],
                                [2,1,2e6,25],
                                [1,0,2e6,25]]
        
            self.numAccounts = len(self.allocations)