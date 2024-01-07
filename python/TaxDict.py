class TaxDict:
    def __init__(self):
        self.federal = self.Federal()
        self.state = self.State()

    class Federal:
        def __init__(self):
            self.federal = TaxDict.FilingStatus()
            self.fica = self.Fica()
            self.ss = TaxDict.FilingStatus()
            self.capitalGains = TaxDict.FilingStatus()

            self.deductions = self.Deductions()
            self.exemptions = self.Exemptions()

            fedRates = [0.10,0.12,0.22,0.24,0.32,0.35,0.37]
            self.federal.joint.bracketMax       = [22000,89450,190750,364200,462500,693750,1e9]
            self.federal.joint.bracketPerc      = fedRates
            self.federal.separate.bracketMax    = [11000,44725,95375,182100,231250,346875,1e9]
            self.federal.separate.bracketPerc   = fedRates
            self.federal.single.bracketMax      = [11000,44725,95375,182100,231250,578125,1e9]
            self.federal.single.bracketPerc     = fedRates
            
            # https://www.ssa.gov/oact/cola/cbb.html
            ssRate = 0.062
            ssSal = 160200
            self.fica.ss.joint.maxSal = ssSal*2
            self.fica.ss.joint.rate = ssRate
            self.fica.ss.separate.maxSal = ssSal*2
            self.fica.ss.separate.rate = ssRate
            self.fica.ss.single.maxSal = ssSal
            self.fica.ss.single.rate = ssRate
            
            medRate = 0.0145
            medAddRate = 0.009            
            self.fica.med.joint.maxSal = 250000
            self.fica.med.joint.rate = medRate
            self.fica.med.joint.addRate = medAddRate
            self.fica.med.separate.maxSal = 125000
            self.fica.med.separate.rate = medRate
            self.fica.med.separate.addRate = medAddRate
            self.fica.med.single.maxSal = 200000
            self.fica.med.single.rate = medRate
            self.fica.med.single.addRate = medAddRate
            
            ssRates = [0, 0.5, 0.85]
            self.ss.joint.bracketMax = [32000, 44000, 1e9]
            self.ss.joint.bracketPerc = ssRates
            self.ss.separate.bracketMax = [25000, 34000, 1e9]
            self.ss.separate.bracketPerc = ssRates
            self.ss.single.bracketMax = [25000, 34000, 1e9]
            self.ss.single.bracketPerc = ssRates

            cgRates = [0, 0.15, 0.2]
            self.capitalGains.joint.bracketMax = [89250, 553850, 1e9]
            self.capitalGains.joint.bracketPerc = cgRates
            self.capitalGains.separate.bracketMax = [44625, 276900, 1e9]
            self.capitalGains.separate.bracketPerc = cgRates
            self.capitalGains.single.bracketMax = [44625, 492300, 1e9]
            self.capitalGains.single.bracketPerc = cgRates
        
        class Fica:
            def __init__(self):
                self.ss = TaxDict.FilingStatus()
                self.med = TaxDict.FilingStatus()
        
        class Deductions:
            def __init__(self):
                self.itemized = self.Itemized()
                self.standard = self.Standard()
            
            class Itemized:
                def __init__(self):
                    # Max per couple OR individual
                    self.maxSalt = 10000 
                    self.maxHouse = 750000
            
            class Standard:
                def __init__(self):
                    # Max per individual
                    self.maxFed = 13800
        
        class Exemptions:
            pass
            # NO FEDERAL EXEMPTIONS
    
    class State:
        def __init__(self):
            self.md = self.Args()
            self.nj = self.Args()
            self.none = self.Args()
            
            # Maryland
            mdRates = [0.02,0.03,0.04,0.0475,0.05,0.0525,0.055,0.0575]
            self.md.state.joint.bracketMax     = [1000,2000,3000,150000,175000,225000,300000,1e9]
            self.md.state.joint.bracketPerc    = mdRates
            self.md.state.separate.bracketMax  = [1000,2000,3000,100000,125000,150000,250000,1e9]
            self.md.state.separate.bracketPerc = mdRates
            self.md.state.single.bracketMax    = [1000,2000,3000,100000,125000,150000,250000,1e9]
            self.md.state.single.bracketPerc   = mdRates
            
            self.md.local.localPerc = 0.025
            
            self.md.deductions.standard.basePerc  = 0.15
            self.md.deductions.standard.stdDedMin = 1500
            self.md.deductions.standard.stdDedMax = 2250
            
            self.md.exemptions.persExempt.joint.bracketMax       = [150000,175000,200000,1e9]
            self.md.exemptions.persExempt.joint.bracketAmt       = [3200,1600,800,0]
            self.md.exemptions.persExempt.separate.bracketMax    = [100000,125000,150000,1e9]
            self.md.exemptions.persExempt.separate.bracketAmt    = [3200,1600,800,0]
            self.md.exemptions.persExempt.single.bracketMax      = [100000,125000,150000,1e9]
            self.md.exemptions.persExempt.single.bracketAmt      = [3200,1600,800,0]
            
            self.md.exemptions.childExempt.joint.bracketMax      = [150000,175000,200000,1e9]
            self.md.exemptions.childExempt.joint.bracketAmt      = [3200,1600,800,0]
            self.md.exemptions.childExempt.separate.bracketMax   = [100000,125000,150000,1e9]
            self.md.exemptions.childExempt.separate.bracketAmt   = [3200,1600,800,0]
            self.md.exemptions.childExempt.single.bracketMax     = [100000,125000,150000,1e9]
            self.md.exemptions.childExempt.single.bracketAmt     = [3200,1600,800,0]
                
            # New Jersey
            njRates = [0.014,0.0175,0.035,0.05525,0.0637,0.0897,0.1075]
            self.nj.state.joint.bracketMax     = [20000,50000,70000,80000,150000,500000,1000000,1e9]
            self.nj.state.joint.bracketPerc    = [0.014,0.0175,0.0245,0.035,0.05525,0.0637,0.0897,0.1075]
            self.nj.state.separate.bracketMax  = [20000,35000,40000,75000,500000,1000000,1e9]
            self.nj.state.separate.bracketPerc = njRates
            self.nj.state.single.bracketMax    = [20000,35000,40000,75000,500000,1000000,1e9]
            self.nj.state.single.bracketPerc   = njRates
            
            self.nj.local.localPerc = 0
            
            self.nj.deductions.standard.basePerc  = 0
            self.nj.deductions.standard.stdDedMin = 0
            self.nj.deductions.standard.stdDedMax = 0
            
            self.nj.exemptions.persExempt.joint.bracketMax       = [1e9]
            self.nj.exemptions.persExempt.joint.bracketAmt       = [1000]
            self.nj.exemptions.persExempt.separate.bracketMax    = [1e9]
            self.nj.exemptions.persExempt.separate.bracketAmt    = [1000]
            self.nj.exemptions.persExempt.single.bracketMax      = [1e9]
            self.nj.exemptions.persExempt.single.bracketAmt      = [1000]
            
            self.nj.exemptions.childExempt.joint.bracketMax      = [1e9]
            self.nj.exemptions.childExempt.joint.bracketAmt      = [1500]
            self.nj.exemptions.childExempt.separate.bracketMax   = [1e9]
            self.nj.exemptions.childExempt.separate.bracketAmt   = [1500]
            self.nj.exemptions.childExempt.single.bracketMax     = [1e9]
            self.nj.exemptions.childExempt.single.bracketAmt     = [1500]
            
            # None
            self.none.state.none.bracketMax = [1e9]
            self.none.state.none.bracketPerc = [0]
            
            self.none.local.localPerc = 0
        
        class Args:    
            def __init__(self):
                self.state = TaxDict.FilingStatus()
                self.local = self.LocalTax()
                self.capitalGains = TaxDict.FilingStatus()

                self.deductions = self.Deductions()
                self.exemptions = self.Exemptions()
            
            class LocalTax:
                def __init__(self):
                    self.localPerc = []
            
            class Deductions:
                def __init__(self):
                    self.itemized = self.Itemized()
                    self.standard = self.Standard()

                class Itemized:
                    pass
                    # NO STATE ITEMIZED DEDUCTIONS

                class Standard:
                    def __init__(self):
                        self.basePerc = []
                        self.stdDedMin = []
                        self.stdDedMax = []
            
            class Exemptions:
                def __init__(self):
                    self.persExempt = TaxDict.FilingStatus()
                    self.childExempt = TaxDict.FilingStatus()
            
    class FilingBracket:
        def __init__(self):
            self.bracketMax = []
            self.bracketPerc = []
            self.bracketAmt = []

    class FilingStatus:
        def __init__(self):
            self.joint = TaxDict.FilingBracket()
            self.separate = TaxDict.FilingBracket()
            self.single = TaxDict.FilingBracket()

            self.none = TaxDict.FilingBracket()