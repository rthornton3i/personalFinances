package com.personalfinances;


public class Vars {
    Base base = new Base();
    Salary salary = new Salary();
    Filing filing = new Filing();
    Children children = new Children();
    
    Expenses expenses = new Expenses();  
    
    Benefits benefits = new Benefits();
    Taxes taxes = new Taxes();
    Savings savings = new Savings();
    Allocations allocations = new Allocations();
    
    public class Base {
        int loops = 100;
        int years = 60; // Starting 2021
        int[] baseAges = {25,25};
        int[] retAges = {50,50};
        
        int[][] ages;
        
        int numInd = baseAges.length;
    }
    
    public class Filing {
        String filingType = "SEPARATE";
        String[] filingState = {"NJ","NJ"};
    }
    
    public class Salary {
        int[] salBase   = {87406,95000};
        int[][] prevSal = {{75000,79750},{83000,87720}};

        double[] salGrowth = {0.025,0.032,0.05};
        
        int[][] salary;
        int[][] income;
        int[] grossIncome;
    }
    
    public class Children {
        int[] childYrs = {4,6};
        int maxChildYr = 22;
        
        int[][] childAges;
    }
    
    public class Expenses {
        Cars cars = new Cars();
        Housing housing = new Housing();
        
        Food food = new Food();
        Entertain entertain = new Entertain();
        PersonalCare personalCare = new PersonalCare();
        Healthcare healthcare = new Healthcare();
        Pet pet = new Pet();
        
        Holiday holiday = new Holiday();
        Charity charity = new Charity();
        
        Education education = new Education();
        Vacation vacation = new Vacation();
        Major major = new Major();
        Random random = new Random();
        
        int[] totalExp;
        int[][] totalExpenses;
        
        int numExpenses = 13;
        
        public class Cars {        
//                           Rich  , Becca , CO1   , S1    , CO2   , S2    , Ch1   , Ch2   , S3a   , S3b     S4a   , S4b        
            int[] purYr   = {-3    , -3    , 5     , 7     , 13    , 16    , 22    , 24    , 21    , 24    , 29    , 32};     
            int[] sellYr  = {5     , 7     , 13    , 16    , 21    , 24    , -1    , -1    , 29    , 32    , -1    , -1};     
            int[] term    = {5     , 5     , 5     , 5     , 5     , 5     , 5     , 5     , 5     , 5     , 5     , 5};
            int[] prin    = {23500 , 19500 , 25000 , 25000 , 30000 , 30000 , 22500 , 22500 , 35000 , 35000 , 40000 , 40000};  
            int[] down    = {20    , 20    , 20    , 20    , 20    , 20    , 20    , 20    , 20    , 20    , 20    , 20};  
            double[] app  = {-20   , -20   , -20   , -20   , -20   , -20   , -20   , -20   , -20   , -20   , -20   , -20};
            double[] rate = {1.9   , 1.9   , 1.9   , 1.9   , 1.9   , 1.9   , 1.9   , 1.9   , 1.9   , 1.9   , 1.9   , 1.9};

            int preBal = 0;
            int preWth = 0;
            
            // Total cost per month
            int insurance = 170+160;
            // Percent of worth (payment**)
            double repairs = 0.025; //{100,400,2500};
            
            // Additional cost relative to pre-child expense
            double insRepChildFactor = 0.35;

            // Total cost per month
            int fuel   = 150;
            int ezpass = (3*20) + (10*4);
            
            // Additional cost relative to pre-child expense
            double fuelEzChildFactor = 0.25;

            int[] carBal;
            int[] carPay;
            int[] carPrn;
            int[] carInt;
            int[] carWth;
            int[] carDwn;
            
            int[] totalCar;

            int numCars = purYr.length;
        }

        public class Housing {
            Rent rent = new Rent();
            House house = new House();

            public class Rent {
                int[] rentYr = {0,0};
                
                // Total cost per month
                int baseRent = 2100;
                int rentFees = 75 + 50 + 25; // Parking, Pet, Trash
                double rentInc = 0.05;
                
                double repairs = 50;
                double insurance = 20;
                
                double electricity = 140;
                double gas = 20;      
                double water = 40;
                
                int[] totalRent;
            }

            public class House {            
                int[] purYr   = {1      , 18     , 33};
                int[] sellYr  = {18     , 33     , -1};
                int[] term    = {30     , 20     , 15};
                double[] rate = {3.25   , 4      , 3.25};
                int[] prin    = {450000 , 750000 , 1250000};
                double[] down = {20     , 20     , 20};
                double[] app  = {2.75   , 2.75   , 2.75};

                int preBal = 0;
                int preWth = 0;
                
                // Percent of worth
                double propTax = 0.0195;
                double repairs  = 0.0125;
                double insurance = 0.005;
                
                // Total cost per month
                double electricity = 150;
                double gas = 30;          
                double water = 50;

                int[] houseBal;
                int[] housePay;
                int[] housePrn;
                int[] houseInt;
                int[] houseWth;
                int[] houseDwn;
                
                int[] totalHouse;
                        
                int numHouses = purYr.length;
            }
        }
        
        public class Food {
            // Total cost per month
            int groceries = 600;
            int restaurants = 200;
            
            // Additional cost relative to pre-child expense
            double childFactor = 0.4;
            // Overall growth after 'years'
            double growthFactor = 0.2;
            
            int[] totalFood;
        }
        
        public class Entertain {
            // Total cost per month
            int wifi = 40;
            int cell = 80;
            int tv   = 0;
            int subs = 120+0+144+60+70; // Amazon, Netflix, Hulu, Google, Microsoft
            
            // Additional cost relative to pre-child expense
            double childFactor = 0.25;
            // Overall growth after 'years'
            double growthFactor = 0.5;
            
            int[] totalEnt;
        }
        
        public class PersonalCare {
            // Total cost per month
            int clothingShoes = 75;
            int hairMakeup = 60;
            
            // Additional cost relative to pre-child expense
            double childFactor = 0.25;
            // Overall growth after 'years'
            double growthFactor = 0.25;
            
            int[] totalPers;
        }
        
        public class Healthcare {
            // Total cost per month
            int[] drugs = {250/12,15};
            
            // Individual
            int[] deductible = {2000,750};
            double[] coinsurance = {0.3,0.2};
            int[] maxOOP = {5000,4050};
            
            boolean[] hsaOpt = {true,false};
            
            int[] visits = {0,4};
            int[] costs = {50,150,1000};
            
            // Additional cost relative to pre-child expense
            double childFactor = 0.25;
            // Overall growth after 'years'
            double growthFactor = 0.25;
            
            int[] totalHealth;
        }
        
        public class Pet {
            // Total cost per month
            int food = 75;
            int essentials = 20;
            int toys = 15;
            int careTaker = 0;
            int vet = (100+250)/12;
            int insurance = 30;
                    
            // Overall growth after 'years'
            double growthFactor = 1.5;
            
            int[] totalPet;
        }
        
        public class Holiday {
            // Overall growth after 'years'
            double familyGrowthFactor = 0.5;
            double childGrowthFactor = 2;
            
            // Cost per year
            int familyBday = 500;
            int familyXmas = 1000;
            
            // Cost per year per child
            int childBday = 100;
            int childXmas = 300;
            
            // Cost per year per person
            int persBday = 100;
            int persXmas = 200;
            int persVal = 100;
            int persAnniv = 150;
            
            int[] totalHol;
        }
        
        public class Charity {
            double baseChar = 0.01;
            
            // Overall growth after 'years'
            double growthFactor = 3;
            
            int[] totalChar;
        }
        
        public class Education {
            // Cost per year per child
            int tuition = 50000;
            int housing = 12000;
            int dining = 3000;
            int books = 1500;
            
            int[] totalEd;
        }
        
        public class Vacation {
            int travel = 400; // Cost per person
            
            int food = 25 + 20 + 40; // Cost per day per person
            int events = 50; // Cost per day per person
            
            int hotel = 300; // Cost per day
            int carRental = 60; // Cost per day
            
            int numDays = 5;
            
            // Overall growth after 'years'
            double growthFactor = 1;
            
            int[] totalVac;
        }
        
        public class Major {
            int[] totalMajor;
            
            int[][] wedding =  {{0,7000},
                                {0,11000},
                                {1,35000}};
        }
        
        public class Random {
            int maxExp = 50000;
            int decayFactor = 4;
            int binWid = 5;
            
            int[] totalRand;
        }
    }
    
    public class Benefits {
        Health health = new Health();
        Retirement retirement = new Retirement();
        SocialSecurity socialSecurity = new SocialSecurity();
        
        public class Health {
            // Cost per year per individual
            int hsa = 0*12;
            int fsa = 0*12;
            int hra = 0*12;    
            
            int medicalPrem = (984 + 1512);
            int visionPrem = (110*2);
            int dentalPrem = (33*2);
            
            // Additional cost relative to pre-child expense
            double childFactor = 0.25;
            // Overall growth after 'years'
            double growthFactor = 0.25;
            
            int[][] healthDed;
            int[][] healthBen;
        }
        
        public class Retirement {
            Args traditional = new Args();
            Args roth = new Args();
            Args match = new Args();
            
            int[] netTradRet;
            int[] netRothRet;
            
            public Retirement() {
                traditional.basePerc = 0; // MAKE PER PERSON
                traditional.growthPerc = 0;
                traditional.binWid = 5;
                traditional.maxCont = 19000;
                
                roth.basePerc = 0.08;
                roth.growthPerc = 0.01;
                roth.binWid = 5;
                roth.maxCont = 19000;
                
                match.maxCont = 19000;
                match.maxPerc = 0.06;
            }
            
            public class Args {
                double basePerc;
                double growthPerc;
                int binWid;
                int maxCont;
                double maxPerc;
                
                int[][] contribution;
            }
        }
        
        public class SocialSecurity {
            int[] collectionAge = {70,70};
            
            int fra = 67;
            double[] fraEarly = {(double) 5/900,(double) 5/1200};
            double fraLate = (double) 5/900;
                    
            double wageInd = 0.0325;
            double cola = 0.0138;
            
            double[] bendPerc = {0.9,0.32,0.15};
            int[] bendPts = {996,6002};
            double[][] bendSlope = {{0.33,25},{1.99,155}};
        
            int[][] ssIns;
        }
    }
    
    public class Taxes {
        Federal federal = new Federal();
        State state = new State();
        
        int[] totalTaxes;
        int[] totalDeducted;
        int[] totalWithheld;
        int[] netIncome;
        int[] netCash;

        public class Federal {
            Fica fica = new Fica();
            Deductions deductions = new Deductions();
            Exemptions exemptions = new Exemptions();
            
            int[][] grossIncomeFed;
            int[][] fedTax;
            int[][] ficaTax;

            public class Fica {
                SS ss = new SS();
                MED med = new MED();

                public class SS {
                    int[][] ssTax;
                }

                public class MED {
                    int[][] medTax;
                }
            }

            public class Deductions {
                Itemized itemized = new Itemized();
                Standard standard = new Standard();

                public class Itemized {
                    int[][] itemDedFed;
                }

                public class Standard {
                    int[][] stdDedFed;
                }
            }
            
            public class Exemptions {
                int[][] exemptFed;
            }
        }

        public class State {
            LocalTax local = new LocalTax();
            Deductions deductions = new Deductions();
            Exemptions exemptions = new Exemptions();
            
            int[][] grossIncomeState;
            int[][] stateTax;
            
            public class LocalTax {
                int[][] localTax;
            }

            public class Deductions {
                Itemized itemized = new Itemized();
                Standard standard = new Standard();

                public class Itemized {
                    int[][] itemDedState;
                }

                public class Standard {
                    int[][] stdDedState;
                }
            }
            
            public class Exemptions {
                PersExempt persExempt = new PersExempt();
                ChildExempt childExempt = new ChildExempt();
                
                public class PersExempt {
                    int[][] persExemptState;
                }

                public class ChildExempt {
                    int[][] childExemptState;
                }
            }
        }
    }
    
    public class Savings {
        double[][] allocations;
        double[][] earnings;
        int[][] contributions;
        int[][] savings;
    }
    
    public class Allocations {
        String[] accountType = {"INVESTING",
                                "INVESTING",
                                "INVESTING",
                                "INVESTING",
                                "INVESTING",
                                "INVESTING",
                                "INVESTING",
                                "INVESTING",
                                "SAVINGS",
                                "SAVINGS",
                                "SAVINGS"};
        
        String[] capGainsType = {"LONG",
                                 "LONG",
                                 "LONG",
                                 "LONG",
                                 "SHORT",
                                 "NONE",
                                 "SHORT",
                                 "NONE",
                                 "NONE",
                                 "NONE",
                                 "NONE"};
        
        int[] baseSavings = {(int) (0.15*29000),             //hiDiv      
                             (int) (0.15*29000),             //lowVol   
                             (int) (0.10*29000),             //valueGrowth   
                             (int) (0.10*29000),             //sectorInd
                             (int) (0.50*29000),             //swingDay    (Vanguard-TEMP)
                             9000 + 19500 + 17500,           //retRoth401  (L3Harris, NG, L'Oreal)
                             0,                              //retTrad401 
                             1700,                           //col529      (Fidelity)
                             73000 + 30000,                  //longTerm    (Goldman Sach's)
                             7000 + 10000,                   //shortTerm   (PNC Growth, BoA Savings)
                             5000 + 10000};                  //spend       (PNC Spend, BoA Spend)
        
        double[][] allocations = {{1 , 1 , 2 , 3 , 3},     // 0 - hiDiv
                                  {1 , 1 , 2 , 3 , 3},     // 1 - lowVol
                                  {1 , 2 , 3 , 1 , 0},     // 2 - valueGrowth
                                  {1 , 2 , 2 , 1 , 0},     // 3 - sectorInd
                                  {4 , 2 , 1 , 0 , 0},     // 4 - swingDay
                                  {0 , 0 , 0 , 0 , 0},     // 5 - retRoth401
                                  {0 , 0 , 0 , 0 , 0},     // 6 - retTrad401
                                  {3 , 8 , 9 , 0 , 0},     // 7 - col529
                                  {5 , 8 , 5 , 3 , 10},    // 8 - longTerm
                                  {3 , 5 , 5 , 3 , 3},     // 9 - shortTerm
                                  {10, 10, 10, 10, 5}};   // 10 - spend
        
                              // Mean, Std
        double[][] earnings = {{4.0,0.5},
                               {8.0,2.5},
                               {10.0,3.0},
                               {10.0,15.0},
                               {30.0,30.0},
                               {10.0,3.0,4.0,1.0},
                               {10.0,3.0,4.0,1.0},
                               {8.0,3.0,5.0,2.0},
                               {1.5,0.5},
                               {0.05,0.01},
                               {0.01,0.01}};
        
                            // To, From, [OPT] Yr
        int[][][] underflow = {{{10},{9}},
                               {{9},{8}},
                               {{8},{4,3,2,1,0}},
                               {{7},{4,3,2,1,0}}};
        
                           // From, To, Max, [OPT] Yr
        int[][] overflow = {{4,3,(int) 250e3},
                            {4,3,0,15},
                            {3,2,(int) 2e6},
                            {2,1,(int) 2e6,25},
                            {1,0,(int) 2e6,25}};
        
        int numAccounts = allocations.length;
    }
}          