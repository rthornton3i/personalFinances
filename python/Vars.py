import pandas as pd
import numpy as np

from numpy.typing import NDArray
from pandas import DataFrame

class Inputs():
    file = 'Inputs/Inputs_ThorntonParents.xlsx'

    """BASE"""
    inputSheet = 'Inputs'
    salarySheet = 'Salary'
    socialSecuritySheet = 'Social Security'

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
    activitiesSheet = 'Activities'
    shoppingSheet = 'Shopping'
    subsSheet = 'Subscriptions'
    personalCareSheet = 'Personal Care'
    healthCareSheet = 'Health Care'
    petSheet = 'Pet'
    giftsSheet = 'Gifts'
    educationSheet = 'Education'
    vacationSheet = 'Vacation'
    majorSheet = 'Major'
    randomSheet = 'Random'

def dropnan(vals):
    return vals[~pd.isna(vals)]

def getValue(file:str,sheet:str,row:int,col:int):
    return pd.read_excel(file,sheet,header=None,skiprows=row-1,usecols=col,nrows=1).iloc[0,0]

def otherFields(data:pd.DataFrame,ignoreFields:list[str]):
    return np.sum([budget.values[0] if not field in ignoreFields else 0 for field,budget in data.iterrows()])

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

    class Base(Inputs):
        def __init__(self):
            super().__init__()

            inputFields = pd.read_excel(self.file,self.inputSheet,header=None,index_col=0,skiprows=1,usecols='A,C:D',nrows=26,names=None)
            
            self.loops:int = inputFields.loc['Iterations'].values[0]
            self.years:int = inputFields.loc['Years'].values[0]

            self.baseAges:list[int] = inputFields.loc['Ages'].values[0:].astype(int)
            self.retAges:list[int]  = inputFields.loc['Retirement Age'].values[0:].astype(int)
            
            self.numInd = len(self.baseAges)

            self.ages:list[int]
            self.isRetire:list[bool]
    
    class Filing(Inputs):
        def __init__(self):
            super().__init__()

            inputFields = pd.read_excel(self.file,self.inputSheet,header=None,index_col=0,skiprows=1,usecols='A,C',nrows=26,names=None)
            
            self.filingType:str  = inputFields.loc['Filing'].values[0]
            self.filingState:str = inputFields.loc['Filing State'].values[0]

            self.iters:int
    
    class Salary(Inputs):
        def __init__(self):
            super().__init__()

            inputFields = pd.read_excel(self.file,self.inputSheet,header=None,index_col=0,skiprows=1,nrows=24,names=None).drop(columns=1)

            self.salOpt:list[str]    = dropnan(inputFields.loc['Salary Option'].values[0:])
            self.salBase:list[float] = dropnan(inputFields.loc['Salary'].values[0:])

            self.salGrowth:list[float] = inputFields.loc['Salary Growth'].values[0:3]
            self.salBonus:list[float]  = inputFields.loc['Bonus'].values[0:3]

            self.promotionChance:float       = inputFields.loc['Chance of Promotion'].values[0]
            self.promotionWaitPeriod:float   = inputFields.loc['Promotion Wait Period'].values[0]
            self.promotionGrowth:list[float] = inputFields.loc['Promotion Growth'].values[0:3]

            self.wageInd:float = inputFields.loc['Inflation Average'].values[0]
            self.wageDev:float = inputFields.loc['Inflation Std Dev'].values[0]

            self.salCustom = pd.read_excel(self.file,self.salarySheet,header=None,skiprows=1,index_col=0,names=None) if any([opt.upper() == 'CUSTOM' for opt in self.salOpt]) else None
            self.prevSal = pd.read_excel(self.file,self.socialSecuritySheet,header=None,skiprows=1,index_col=0,names=None).sort_index()

            self.salary:list[float]
            self.income:list[float]
            self.inflation:list[float]
            self.summedInflation:list[float]
    
    class Children(Inputs):
        def __init__(self):
            super().__init__()

            inputFields = pd.read_excel(self.file,self.inputSheet,header=None,index_col=0,skiprows=1,nrows=26,names=None).drop(columns=1)

            self.childBaseAges     = dropnan(inputFields.loc['Child Ages'].values[0:]).astype(int)
            self.maxChildYr        = inputFields.loc['Max Age of Childcare'].values[0]
            self.childInflationVal = inputFields.loc['Child Inflation'].values[0]

            self.childAges:list[int]
            self.isKids:list[int]
            self.childInflation:list[float]

    class Expenses:
        def __init__(self):
            self.loans = self.Loans()
            self.cars = self.Cars()
            self.house = self.House()
            self.rent = self.Rent()
            
            self.food = self.Food()
            self.shopping = self.Shopping()
            self.activities = self.Activities()

            self.subscriptions = self.Subscriptions()
            self.personalCare = self.PersonalCare()
            self.healthcare = self.Healthcare()
            self.pet = self.Pet()
            
            self.gifts = self.Gifts()
            
            self.education = self.Education()
            self.vacation = self.Vacation()
            self.major = self.Major()
            self.random = self.Random()

            self.exps = [e for e in dir(self) if not e.startswith('__') and 
                                                 not callable(getattr(self, e)) and 
                                                 hasattr(getattr(self,e),'allocation')]

            self.totalExpenses:DataFrame
        
        class Loans(Inputs):
            def __init__(self):
                super().__init__()

                self.loanSummary = pd.read_excel(self.file,self.loanSheet,header=1,usecols='A:D',
                                                names=['loanYr','prin','term','rate']).dropna()
                
                self.allocation:str = getValue(self.file,self.loanSheet,row=2,col='G')
            
                self.numLoans = self.loanSummary.shape[0]

                self.loanBal:list[float]
                self.loanPay:list[float]
                self.loanPrn:list[float]
                self.loanInt:list[float]

        class Cars(Inputs):
            def __init__(self):
                super().__init__()

                self.carSummary = pd.read_excel(self.file,self.carSheet,header=1,usecols='A:G',
                                                names=['purYr','sellYr','prin','down','app','term','rate']).dropna().reset_index(drop=True)
                
                self.allocation:str = getValue(self.file,self.carSheet,row=7,col='J')

                carFields = pd.read_excel(self.file,self.carSheet,header=None,index_col=0,skiprows=1,usecols='I,K:M',nrows=4,names=None)
                self.insurance  = carFields.loc['Insurance'].values[0]
                self.repairs    = carFields.loc['Repairs'].values[0:]
                self.fuel       = carFields.loc['Fuel'].values[0]
                self.ezpass     = carFields.loc['EZ Pass'].values[0]
            
                self.numCars = self.carSummary.shape[0]

                self.carBal:list[float]
                self.carPay:list[float]
                self.carPrn:list[float]
                self.carInt:list[float]
                self.carWth:list[float]
                self.carDwn:list[float]

        class Rent(Inputs):
            def __init__(self):
                super().__init__()
                
                rentFields = pd.read_excel(self.file,self.rentSheet,header=None,index_col=0,skiprows=1,names=None).drop(columns=1)
            
                self.allocation:str = getValue(self.file,self.rentSheet,row=13,col='B')

                self.rentYr   = dropnan(rentFields.loc['Rent Years'].values[0:2])
                self.baseRent = rentFields.loc['Base Rent'].values[0]
                self.rentFees = dropnan(rentFields.loc['Rent Fees'].values[0:])
                
                self.repairs   = rentFields.loc['Repairs'].values[0:3]
                self.insurance = rentFields.loc['Insurance'].values[0]
                
                self.electricity = rentFields.loc['Electricity'].values[0]
                self.gas         = rentFields.loc['Gas'].values[0]      
                self.water       = rentFields.loc['Water'].values[0]
            
        class House(Inputs):
            def __init__(self):
                super().__init__()
                
                self.houseSummary = pd.read_excel(self.file,self.homeSheet,header=1,usecols='A:G',
                                            names=['purYr','sellYr','prin','down','app','term','rate']).dropna()
            
                self.allocation:str = getValue(self.file,self.homeSheet,row=10,col='J')

                homeFields = pd.read_excel(self.file,self.homeSheet,header=None,index_col=0,skiprows=1,usecols='I,K:M',nrows=7,names=None)
                self.propTax        = homeFields.loc['Property Tax'].values[0]
                self.insurance      = homeFields.loc['Insurance'].values[0]
                self.repairs        = homeFields.loc['Repairs'].values[0:]
                self.electricity    = homeFields.loc['Electricity'].values[0]
                self.gas            = homeFields.loc['Gas'].values[0]
                self.water          = homeFields.loc['Water'].values[0]
                self.sewage         = homeFields.loc['Sewage'].values[0]
                        
                self.numHouses = self.houseSummary.shape[0]

                self.houseBal:list[float]
                self.housePay:list[float]
                self.housePrn:list[float]
                self.houseInt:list[float]
                self.houseWth:list[float]
                self.houseDwn:list[float]
            
        class Food(Inputs):
            def __init__(self):
                super().__init__()

                self.allocation:str = getValue(self.file,self.foodSheet,row=2,col='F')

                foodFields = pd.read_excel(self.file,self.foodSheet,header=None,index_col=0,skiprows=1,usecols='A,C',names=None)
                self.groceries   = foodFields.loc['Groceries'].values[0]
                self.restaurants = foodFields.loc['Restaurants'].values[0]
                self.other       = otherFields(foodFields,['Groceries','Restaurants'])
        
        class Shopping(Inputs):
            def __init__(self):
                super().__init__()

                self.allocation:str = getValue(self.file,self.shoppingSheet,row=2,col='F')

                shoppingFields = pd.read_excel(self.file,self.shoppingSheet,header=None,index_col=0,skiprows=1,usecols='A,C',names=None)
                self.general = shoppingFields.loc['General Merchandise'].values[0]
                self.other   = otherFields(shoppingFields,['General Merchandise'])
        
        class Activities(Inputs):
            def __init__(self):
                super().__init__()

                self.allocation:str = getValue(self.file,self.activitiesSheet,row=2,col='F')

                activityFields = pd.read_excel(self.file,self.activitiesSheet,header=None,index_col=0,skiprows=1,usecols='A,C',names=None)
                self.social  = activityFields.loc['Social Events'].values[0]
                self.hobbies = activityFields.loc['Hobbies'].values[0]
                self.sports  = activityFields.loc['Sports'].values[0]
                self.other   = otherFields(activityFields,['Social Events','Hobbies','Sports'])
        
        class Subscriptions(Inputs):
            def __init__(self):
                super().__init__()

                self.allocation:str = getValue(self.file,self.subsSheet,row=8,col='B')

                subsFields = pd.read_excel(self.file,self.subsSheet,header=None,index_col=0,skiprows=1,nrows=5,names=None).drop(columns=1)
                self.internet:float          = subsFields.loc['Internet'].values[0]
                self.phone:float             = subsFields.loc['Phone'].values[0]
                self.tv:list[float]          = dropnan(subsFields.loc['Television'].values[0:])
                self.software:list[float]    = dropnan(subsFields.loc['Software'].values[0:])
                self.memberships:list[float] = dropnan(subsFields.loc['Memberships'].values[0:])
            
        class PersonalCare(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation:str = getValue(self.file,self.personalCareSheet,row=2,col='F')

                personalCareFields = pd.read_excel(self.file,self.personalCareSheet,header=None,index_col=0,skiprows=1,nrows=5,names=None).drop(columns=1)
                self.clothing:float    = personalCareFields.loc['Clothing'].values[0]
                self.shoes:float       = personalCareFields.loc['Shoes'].values[0]
                self.laundry:float     = personalCareFields.loc['Laundry'].values[0]
                self.hair:float        = personalCareFields.loc['Hair'].values[0]
                self.other:list[float] = otherFields(personalCareFields,['Clothing','Shoes','Laundry','Hair'])
        
        class Healthcare(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation:str = getValue(self.file,self.healthCareSheet,row=14,col='B')

                insuranceFields = pd.read_excel(self.file,self.healthCareSheet,header=None,index_col=0,skiprows=1,nrows=11,names=None).drop(columns=1)
                self.premium:list[float]     = dropnan(insuranceFields.loc['Premium'].values[0:])
                self.deductible:list[float]  = dropnan(insuranceFields.loc['Deductible'].values[0:])
                self.coinsurance:list[float] = dropnan(insuranceFields.loc['Coinsurance'].values[0:])
                self.maxOOP:list[float]      = dropnan(insuranceFields.loc['Max Out-of-Pocket'].values[0:])
                
                self.visits:list[int]  = insuranceFields.loc['# of Visits'].values[0:3]
                self.costs:list[float] = insuranceFields.loc['Cost per Visit'].values[0:3]
                self.drugs:float       = insuranceFields.loc['Pharmacy'].values[0]

                self.hsaOpt:bool      = insuranceFields.loc['HSA'].values[0]
                self.hsaDeposit:float = insuranceFields.loc['HSA Deposit'].values[0]
            
        class Pet(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation:str = getValue(self.file,self.petSheet,row=2,col='F')

                petFields = pd.read_excel(self.file,self.petSheet,header=None,index_col=0,skiprows=1,nrows=5,names=None).drop(columns=1)
                self.food:float        = petFields.loc['Food'].values[0]
                self.essentials:float  = petFields.loc['Essentials'].values[0]
                self.toys:float        = petFields.loc['Toys'].values[0]
                self.vet:float         = petFields.loc['Vet'].values[0]
                self.other:list[float] = otherFields(petFields,['Food','Essentials','Toys','Vet'])
        
        class Gifts(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation:str = getValue(self.file,self.giftsSheet,row=7,col='B')

                giftsFields = pd.read_excel(self.file,self.giftsSheet,header=None,index_col=0,skiprows=1,nrows=4,names=None).drop(columns=1)
                self.donations:float       = giftsFields.loc['Donations'].values[0]
                self.birthdays:list[float] = dropnan(giftsFields.loc['Birthdays'].values[0:])
                self.holidays:list[float]  = dropnan(giftsFields.loc['Holidays'].values[0:])
        
        class Education(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation:str = getValue(self.file,self.educationSheet,row=7,col='B')

                educationFields = pd.read_excel(self.file,self.educationSheet,header=None,index_col=0,skiprows=1,nrows=4,names=None).drop(columns=1)
                self.tuition:float = educationFields.loc['Tuition'].values[0]
                self.housing:float = educationFields.loc['Housing'].values[0]
                self.dining:float  = educationFields.loc['Dining'].values[0]
                self.books:float   = educationFields.loc['Books'].values[0]
        
        class Vacation(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation:str = getValue(self.file,self.vacationSheet,row=10,col='B')

                vacationFields = pd.read_excel(self.file,self.vacationSheet,header=None,index_col=0,skiprows=1,nrows=5,names=None).drop(columns=1)
                self.travel:list[float] = vacationFields.loc['Travel'].values[0:3]
                self.hotel:list[float]  = vacationFields.loc['Hotel'].values[0:3]
                self.food:float         = vacationFields.loc['Food'].values[0]
                self.events:float       = vacationFields.loc['Events'].values[0]
                self.carRental:float    = vacationFields.loc['Rental'].values[0]
                
                self.numDays = pd.read_excel(self.file,self.vacationSheet,header=None,skiprows=7,usecols='C:E',nrows=1).iloc[0].values
        
        class Major(Inputs):
            def __init__(self):
                super().__init__()
                
                self.majorSummary = pd.read_excel(self.file,self.majorSheet,header=1,usecols='A,C:D',
                                                  names=['purYr','cost','isRepeat']).dropna()
                
                self.allocation:str = getValue(self.file,self.majorSheet,row=2,col='G')
        
        class Random(Inputs):
            def __init__(self):
                super().__init__()
                
                self.allocation:str = getValue(self.file,self.randomSheet,row=5,col='B')

                randomFields = pd.read_excel(self.file,self.randomSheet,header=None,index_col=0,skiprows=1,nrows=2,names=None).drop(columns=1)
                self.maxExp:float    = randomFields.loc['Max Cost'].values[0]
                self.decayFactor:int = randomFields.loc['Decay Factor'].values[0]             
    
    class Benefits:
        def __init__(self):
            self.health = self.Health()
            self.retirement = self.Retirement()
            self.socialSecurity = self.SocialSecurity()
        
        class Health:
            def __init__(self):
                # Cost per year per individual
                self.hsaLimit = self.Args()
                self.fsaLimit = self.Args()
                self.hraLimit = self.Args()

                self.hsaLimit.single = 4150
                self.hsaLimit.joint = 8300
                self.hsaLimit.catchUp = 1000
                
                self.hsaDeposit:list[float]

            class Args:
                def __init__(self):
                    self.joint:list[float]
                    self.single:list[float]
                    self.catchUp:list[float]
        
        class Retirement:
            def __init__(self):
                self.traditional = self.Args()
                self.roth = self.Args()
                self.match = self.Args()
                
                self.rmdAge = 72
                self.rmdFactor = [0.00962,2.345,144.617]
            
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
                    self.basePerc:list[float]
                    self.maxPerc:list[float]
            
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

                self.ssIns:list[float]
        
    class Taxes:
        def __init__(self):
            self.federal = self.Federal()
            self.state = self.State()            

        class Federal:
            def __init__(self):
                self.fica = self.Fica()
                self.deductions = self.Deductions()
                self.exemptions = self.Exemptions()

            class Fica:
                def __init__(self):
                    self.ss = self.SS()
                    self.med = self.MED()

                class SS:
                    def __init__(self):
                        pass

                class MED:
                    def __init__(self):
                        pass    

            class Deductions:
                def __init__(self):
                    self.itemized = self.Itemized()
                    self.standard = self.Standard()

                class Itemized:
                    def __init__(self):
                        pass

                class Standard:
                    def __init__(self):
                        pass
            
            class Exemptions:
                def __init__(self):
                    pass   

        class State:
            def __init__(self):
                self.local = self.LocalTax()
                self.deductions = self.Deductions()
                self.exemptions = self.Exemptions()
            
            class LocalTax:
                def __init__(self):
                    self.localTax = []            

            class Deductions:
                def __init__(self):
                    self.itemized = self.Itemized()
                    self.standard = self.Standard()

                class Itemized:
                    def __init__(self):
                        pass

                class Standard:
                    def __init__(self):
                        pass
            
            class Exemptions:
                def __init__(self):
                    self.persExempt = self.PersExempt()
                    self.childExempt = self.ChildExempt()
                
                class PersExempt:
                    def __init__(self):
                        pass
                

                class ChildExempt:
                    def __init__(self):
                        pass

    class Savings():
        def __init__(self):
            self.allocations:list[float]
            self.earnings:list[float]
            self.savings:DataFrame
            self.reports = self.Reports()

        class Reports:
            totalTaxes:DataFrame
            totalDeducted:DataFrame
            totalWithheld:DataFrame
            retireIncome:DataFrame
            capitalGains:DataFrame
    
    class Accounts(Inputs):
        def __init__(self):
            super().__init__()
            
            self.allocations = pd.read_excel(self.file,self.allocationsSheet,skiprows=1,index_col=0,header=None)
            self.earnings = pd.read_excel(self.file,self.earningsSheet,skiprows=2,index_col=0,header=None)
            self.accountSummary = pd.read_excel(self.file,self.accountsSheet,skiprows=2,index_col=0,header=None,
                                                names=['baseSavings','accOwner','capGainsType','accountType','overflow','overAmt','underflow'])