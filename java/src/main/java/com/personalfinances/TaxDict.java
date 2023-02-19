package com.personalfinances;


public class TaxDict {
    Federal federal = new Federal();
    State state = new State();

    public class Federal {
        FederalTax federal = new FederalTax();
        Fica fica = new Fica();
        FederalTax ss = new FederalTax();
        Deductions deductions = new Deductions();
        Exemptions exemptions = new Exemptions();
        
        public Federal() {
            federal.joint.bracketMax = new int[]{19050,77400,165000,315000,400000,600000,(int) 1e9};
            federal.joint.bracketPerc = new double[]{0.10,0.12,0.22,0.24,0.32,0.35,0.37};
            federal.separate.bracketMax = new int[]{9525,38700,82500,157500,200000,300000,(int) 1e9};
            federal.separate.bracketPerc = new double[]{0.10,0.12,0.22,0.24,0.32,0.35,0.37};
            federal.single.bracketMax = new int[]{9525,38700,82500,157500,200000,500000,(int) 1e9};
            federal.single.bracketPerc = new double[]{0.10,0.12,0.22,0.24,0.32,0.35,0.37};
            
            fica.ss.joint.maxSal = 142800;
            fica.ss.joint.rate = 0.062;
            fica.ss.separate.maxSal = 142800;
            fica.ss.separate.rate = 0.062;
            fica.ss.single.maxSal = 142800;
            fica.ss.single.rate = 0.062;
            
            fica.med.joint.maxSal = 250000;
            fica.med.joint.rate = 0.0145;
            fica.med.joint.addRate = 0.009;
            fica.med.separate.maxSal = 125000;
            fica.med.separate.rate = 0.0145;
            fica.med.separate.addRate = 0.009;
            fica.med.single.maxSal = 200000;
            fica.med.single.rate = 0.0145;
            fica.med.single.addRate = 0.009;
            
            ss.joint.bracketMax = new int[]{32000, 44000, (int) 1e9};
            ss.joint.bracketPerc = new double[]{0, 0.5, 0.85};
            ss.separate.bracketMax = new int[]{25000, 34000, (int) 1e9};
            ss.separate.bracketPerc = new double[]{0, 0.5, 0.85};
            ss.single.bracketMax = new int[]{25000, 34000, (int) 1e9};
            ss.single.bracketPerc = new double[]{0, 0.5, 0.85};
        }
        
        public class FederalTax {
            Filing joint    = new Filing();
            Filing separate = new Filing();
            Filing single   = new Filing();
            
            public class Filing {
                int[] bracketMax;
                double[] bracketPerc;
            }
        }
        
        public class Fica {
            SS ss = new SS();
            MED med = new MED();
            
            public class SS {
                Filing joint    = new Filing();
                Filing separate = new Filing();
                Filing single   = new Filing();
            }
            
            public class MED {
                Filing joint    = new Filing();
                Filing separate = new Filing();
                Filing single   = new Filing();
            }
            
            public class Filing {
                int maxSal;
                double rate;
                double addRate;
            }
        }
        
        public class Deductions {
            Itemized itemized = new Itemized();
            Standard standard = new Standard();
            
            public class Itemized {
                // Max per couple OR individual
                int maxSlp = 10000; 
                int maxHouse = 750000;
            }
            
            public class Standard {
                // Max per individual
                int maxFed = 12000;
            }
        }
        
        public class Exemptions {
            // NO FEDERAL EXEMPTIONS
        }
    }
    
    public class State {
        Args md = new Args();
        Args nj = new Args();
        Args none = new Args();
            
        public State() {
            // Maryland
            md.state.joint.bracketMax     = new int[]{1000,2000,3000,150000,175000,225000,300000,(int) 1e9};
            md.state.joint.bracketPerc    = new double[]{0.02,0.03,0.04,0.0475,0.05,0.0525,0.055,0.0575};
            md.state.separate.bracketMax  = new int[]{1000,2000,3000,100000,125000,150000,250000,(int) 1e9};
            md.state.separate.bracketPerc = new double[]{0.02,0.03,0.04,0.0475,0.05,0.0525,0.055,0.0575};
            md.state.single.bracketMax    = new int[]{1000,2000,3000,100000,125000,150000,250000,(int) 1e9};
            md.state.single.bracketPerc   = new double[]{0.02,0.03,0.04,0.0475,0.05,0.0525,0.055,0.0575};
            
            md.local.localPerc = 0.025;
            
            md.deductions.standard.basePerc  = 0.15;
            md.deductions.standard.stdDedMin = 1500;
            md.deductions.standard.stdDedMax = 2250;
            
            md.exemptions.persExempt.joint.bracketMax       = new int[]{150000,175000,200000,(int) 1e9};
            md.exemptions.persExempt.joint.bracketAmt       = new int[]{3200,1600,800,0};
            md.exemptions.persExempt.separate.bracketMax    = new int[]{100000,125000,150000,(int) 1e9};
            md.exemptions.persExempt.separate.bracketAmt    = new int[]{3200,1600,800,0};
            md.exemptions.persExempt.single.bracketMax      = new int[]{100000,125000,150000,(int) 1e9};
            md.exemptions.persExempt.single.bracketAmt      = new int[]{3200,1600,800,0};
            
            md.exemptions.childExempt.joint.bracketMax      = new int[]{150000,175000,200000,(int) 1e9};
            md.exemptions.childExempt.joint.bracketAmt      = new int[]{3200,1600,800,0};
            md.exemptions.childExempt.separate.bracketMax   = new int[]{100000,125000,150000,(int) 1e9};
            md.exemptions.childExempt.separate.bracketAmt   = new int[]{3200,1600,800,0};
            md.exemptions.childExempt.single.bracketMax     = new int[]{100000,125000,150000,(int) 1e9};
            md.exemptions.childExempt.single.bracketAmt     = new int[]{3200,1600,800,0};
                
            // New Jersey
            nj.state.joint.bracketMax     = new int[]{20000,50000,70000,80000,150000,500000,5000000,(int) 1e9};
            nj.state.joint.bracketPerc    = new double[]{0.014,0.0175,0.0245,0.035,0.05525,0.0637,0.0897,0.1075};
            nj.state.separate.bracketMax  = new int[]{20000,35000,40000,75000,500000,5000000,(int) 1e9};
            nj.state.separate.bracketPerc = new double[]{0.014,0.0175,0.035,0.05525,0.0637,0.0897,0.1075};
            nj.state.single.bracketMax    = new int[]{20000,35000,40000,75000,500000,5000000,(int) 1e9};
            nj.state.single.bracketPerc   = new double[]{0.014,0.0175,0.035,0.05525,0.0637,0.0897,0.1075};
            
            nj.local.localPerc = 0;
            
            nj.deductions.standard.basePerc  = 0;
            nj.deductions.standard.stdDedMin = 0;
            nj.deductions.standard.stdDedMax = 0;
            
            nj.exemptions.persExempt.joint.bracketMax       = new int[]{(int) 1e9};
            nj.exemptions.persExempt.joint.bracketAmt       = new int[]{1000};
            nj.exemptions.persExempt.separate.bracketMax    = new int[]{(int) 1e9};
            nj.exemptions.persExempt.separate.bracketAmt    = new int[]{1000};
            nj.exemptions.persExempt.single.bracketMax      = new int[]{(int) 1e9};
            nj.exemptions.persExempt.single.bracketAmt      = new int[]{1000};
            
            nj.exemptions.childExempt.joint.bracketMax      = new int[]{(int) 1e9};
            nj.exemptions.childExempt.joint.bracketAmt      = new int[]{1500};
            nj.exemptions.childExempt.separate.bracketMax   = new int[]{(int) 1e9};
            nj.exemptions.childExempt.separate.bracketAmt   = new int[]{1500};
            nj.exemptions.childExempt.single.bracketMax     = new int[]{(int) 1e9};
            nj.exemptions.childExempt.single.bracketAmt     = new int[]{1500};
            
            // None
            none.state.none.bracketMax = new int[]{(int) 1e9};
            none.state.none.bracketPerc = new double[]{0};
            
            none.local.localPerc = 0;
        }
        
        public class Args {            
            StateTax state = new StateTax();
            LocalTax local = new LocalTax();
            Deductions deductions = new Deductions();
            Exemptions exemptions = new Exemptions();
            
            public class StateTax {
                Filing joint = new Filing();
                Filing separate = new Filing();
                Filing single = new Filing();
                
                Filing none = new Filing();
            }
            
            public class LocalTax {
                double localPerc;
            }
            
            public class Deductions {
                Itemized itemized = new Itemized();
                Standard standard = new Standard();

                public class Itemized {
                    // NO STATE ITEMIZED DEDUCTIONS
                }

                public class Standard {
                    double basePerc;
                    int stdDedMin;
                    int stdDedMax;
                }
            }
            
            public class Exemptions {
                PersExempt persExempt = new PersExempt();
                ChildExempt childExempt = new ChildExempt();

                public class PersExempt {
                    Filing joint = new Filing();
                    Filing separate = new Filing();
                    Filing single = new Filing();
                }
                
                public class ChildExempt {
                    Filing joint = new Filing();
                    Filing separate = new Filing();
                    Filing single = new Filing();
                }
            }
            
            public class Filing {
                int[] bracketMax;
                
                double[] bracketPerc;
                int[] bracketAmt;
            }
        }
    }
}