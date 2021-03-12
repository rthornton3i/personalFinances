package com.personalfinances;

import java.lang.Math;

public class Taxes {
    // Public Variables
    static int years;
    static int numInd;
    static int[][] income;
    
    static String filingType;
    static String[] filingState;
    
    static int[][] childAges;
    static int maxChildYr;
    
    static Vars vars;
    static TaxDict taxes;
    
    // Private Variables
    private static int iters;
    
    private static int[][] healthDed;
    private static int[][] healthBen;
    
    private static double[][] perc401;
    
    private static int[][] saltTaxes;
    private static int[][] slpDed;
    private static int[][] mortInt;
    private static int[][] propTax;
    private static int[][] charDon;
    
    private static int[][] itemDedFed;
    private static int[][] itemDedState;
    private static int[][] stdDedFed;
    private static int[][] stdDedState;
    
    private static int[][] exemptFed;
    private static int[][] persExemptState;
    private static int[][] childExemptState;
    
    private static int[][] grossIncomeState;
    private static int[][] grossIncomeFed;
    
    private static int[][] stateTax;
    private static int[][] localTax;
    private static int[][] fedTax;
    private static int[][] ficaTax;
    
    private static int[] totalTaxes;
    private static int[] totalDeducted;
    private static int[] totalWithheld;
    private static int[] netIncome;
    private static int[] netCash;
    private static int[] netTradRet;
    private static int[] netRothRet;
    
    public Taxes(Vars vars, TaxDict taxes) {
        this.vars = vars;
        this.taxes = taxes;
        
        years = vars.base.years;
        numInd = vars.base.numInd;
        income = vars.salary.income;
        
        filingType = vars.filing.filingType;
        filingState = vars.filing.filingState; 
        
        childAges = vars.children.childAges;
        maxChildYr = vars.children.maxChildYr;
    }
        
    public Vars run() {  
        switch (filingType.toUpperCase()) {
            case "JOINT" -> iters = 1;
            case "SEPARATE", "SINGLE" -> iters = numInd;
        }
        
//      Benefits
        healthDed = new int[iters][years];
        healthBen = new int[iters][years];
        
        healthCalc();
        vars.benefits.health.healthDed = healthDed;
        vars.benefits.health.healthBen = healthBen;
        
//      Retirement
        perc401 = new double[iters][years];
        
        vars.benefits.retirement.traditional.contribution = retCalc(vars.benefits.retirement.traditional);
        vars.benefits.retirement.roth.contribution = retCalc(vars.benefits.retirement.roth);
        vars.benefits.retirement.match.contribution = matchCalc(vars.benefits.retirement.match);
        
//      Deduction/Exemptions
        mortInt = new int[iters][years];
        charDon = new int[iters][years];
        slpDed = new int[iters][years];
        
        propTax = new int[iters][years];
        saltTaxes = null;
        
        itemDedFed = new int[iters][years];
        itemDedState = new int[iters][years];
                
        itemDedCalc();
        vars.taxes.federal.deductions.itemized.itemDedFed = itemDedFed;
        vars.taxes.state.deductions.itemized.itemDedState = itemDedState;
        
        stdDedFed = new int[iters][years];
        stdDedState = new int[iters][years];
        
        stdDedCalc();
        vars.taxes.federal.deductions.standard.stdDedFed = stdDedFed; 
        vars.taxes.state.deductions.standard.stdDedState = stdDedState;
        
        exemptFed = new int[iters][years];
        persExemptState = new int[iters][years];
        childExemptState = new int[iters][years];
        
        exemptCalc();
        vars.taxes.federal.exemptions.exemptFed = exemptFed;
        vars.taxes.state.exemptions.persExempt.persExemptState = persExemptState;
        vars.taxes.state.exemptions.childExempt.childExemptState = childExemptState;
        
//      Gross Earnings
        grossIncomeFed = new int[iters][years];
        grossIncomeState = new int[iters][years];
        
        grossEarnCalc();
        
//      State Taxes
        stateTax = new int[iters][years];
        localTax = new int[iters][years];
        
        slTaxCalc();
        vars.taxes.state.stateTax = stateTax;
        vars.taxes.state.local.localTax = localTax;  
        
//      Gross Earnings (Update)
        itemDedCalc();
        grossEarnCalc();
        vars.taxes.federal.grossIncomeFed = grossIncomeFed;
        vars.taxes.state.grossIncomeState = grossIncomeState;
        
//      Federal Taxes
        fedTax = new int[iters][years];
        ficaTax = new int[iters][years];

        fedTaxCalc();
        vars.taxes.federal.fedTax = fedTax;
        vars.taxes.federal.ficaTax = ficaTax;
        
//      Net Income    
        totalTaxes = new int[years];
        totalDeducted = new int[years];
        totalWithheld = new int[years];
        
        netIncome = new int[years];
        netCash = new int[years];
        netTradRet = new int[years];
        netRothRet = new int[years];
                        
        netIncCalc();
        vars.taxes.totalTaxes = totalTaxes;
        vars.taxes.totalDeducted = totalDeducted;
        vars.taxes.totalWithheld = totalWithheld;
        
        vars.taxes.netIncome = netIncome;
        vars.taxes.netCash = netCash;
        vars.benefits.retirement.netTradRet = netTradRet;
        vars.benefits.retirement.netRothRet = netRothRet;

        return vars;
    }
    
    public static void healthCalc() {   
        Vars.Benefits.Health health = vars.benefits.health;
        
        int[][] hsa = new int[iters][years];
        int[][] fsa = new int[iters][years];
        int[][] hra = new int[iters][years];
        int[][] medicalPrem = new int[iters][years];
        int[][] visionPrem  = new int[iters][years];
        int[][] dentalPrem  = new int[iters][years];
        
        for (int i = 0; i < iters; i++) {
            for (int j = 0; j < years; j++) {
                hsa[i][j] = (int) (health.hsa * (1 + ((double) i / years * health.growthFactor)));
                fsa[i][j] = (int) (health.fsa * (1 + ((double) i / years * health.growthFactor)));
                hra[i][j] = (int) (health.hra * (1 + ((double) i / years * health.growthFactor)));
                
                medicalPrem[i][j] = (int) ((health.medicalPrem * (1 + ((double) i / years * health.growthFactor))));
                visionPrem[i][j]  = (int) ((health.visionPrem * (1 + ((double) i / years * health.growthFactor))));
                dentalPrem[i][j]  = (int) ((health.dentalPrem * (1 + ((double) i / years * health.growthFactor))));

                for (int k = 0; k < childAges.length; k++) {
                    if (childAges[k][j] > 0 && childAges[k][j] < maxChildYr) {
                        medicalPrem[i][j] = (int) (medicalPrem[i][j] * (1 + health.childFactor));
                        visionPrem[i][j]  = (int) (visionPrem[i][j] * (1 + health.childFactor));
                        dentalPrem[i][j]  = (int) (dentalPrem[i][j] * (1 + health.childFactor));
                    }
                }
            }
        }
        
        healthDed  = Utility.ArrayMath.sumArrays2(new int[]{iters,years},hsa,fsa,hra);
        healthBen  = Utility.ArrayMath.sumArrays2(new int[]{iters,years},medicalPrem,visionPrem,dentalPrem);
    }
    
    public static int[][] retCalc(Vars.Benefits.Retirement.Args retirement) {        
        double[][] ret401Perc = new double[iters][years];
        
        for (int i = 0; i < iters; i++) {
            for (int j = 0; j < years; j++) {
                ret401Perc[i][j] = retirement.basePerc;
            }
        }
        
        for (int i = 0; i < iters; i++) {
            for (int j = 0; j < years; j++) {
                if (j % retirement.binWid == 0) {
                    for (int n = j; n < years; n++) {
                        ret401Perc[i][n] = ret401Perc[i][n] + retirement.growthPerc;
                    }
                }
            }
        }
        
        perc401 = Utility.ArrayMath.sumArrays2D(new int[]{iters,years},perc401,ret401Perc);        
        int[][] contribution =  Utility.Conversion.double2int2(new int[]{iters,years},
                                    Utility.ArrayMath.multArrays2(new int[]{iters,years},ret401Perc,
                                        Utility.Conversion.int2double2(new int[]{iters,years},income)));
        
        for (int i = 0; i < iters; i++) {
            for (int j = 0; j < years; j++) {
                if (contribution[i][j] > retirement.maxCont) {
                    contribution[i][j] = retirement.maxCont;
                }
            }
        }
        
        return contribution;
    }
    
    public static int[][] matchCalc(Vars.Benefits.Retirement.Args retirement) {        
        double[][] match401Perc = new double[iters][years];
        
        for (int i = 0; i < iters; i++) {
            for (int j = 0; j < years; j++) {
                if (perc401[i][j] <= retirement.maxPerc) {
                    match401Perc[i][j] = perc401[i][j];
                } else {
                    match401Perc[i][j] = retirement.maxPerc;
                }
            }
        }
        
        int[][] contribution =  Utility.Conversion.double2int2(new int[]{iters,years},
                                    Utility.ArrayMath.multArrays2(new int[]{iters,years},match401Perc,
                                        Utility.Conversion.int2double2(new int[]{iters,years},income)));
        
        for (int i = 0; i < iters; i++) {
            for (int j = 0; j < years; j++) {
                if (contribution[i][j] > retirement.maxCont) {
                    contribution[i][j] = retirement.maxCont;
                }
            }
        }
        
        return contribution;
    }
    
    public static void itemDedCalc() {
        TaxDict.Federal.Deductions.Itemized itemDed = taxes.federal.deductions.itemized;
        Vars.Expenses.Housing.House house = vars.expenses.housing.house;
        Vars.Expenses.Charity charity = vars.expenses.charity;

        for (int i = 0; i < iters; i++) {
            for (int j = 0; j < years; j++) {
                // FEDERAL
                // SLP Taxes
                if (saltTaxes != null) {
                    if (saltTaxes[i][j] > itemDed.maxSlp / iters) {
                        slpDed[i][j] = (int) (itemDed.maxSlp / iters);
                    } else {
                        slpDed[i][j] = saltTaxes[i][j];
                    }
                } else {
                    slpDed[i][j] = 0;
                }
                
                // Mortgage Interest
                if (house.houseBal[j] < itemDed.maxHouse / iters) {
                    mortInt[i][j] = (int) (house.houseInt[j] / iters);
                } else {
                    mortInt[i][j] = (int) (((house.houseInt[j] / house.houseBal[j]) * itemDed.maxHouse) / iters);
                }
                
                // Charitable Donations
                charDon[i][j] = (int) (charity.totalChar[j] / iters);
                
                itemDedFed[i][j] = slpDed[i][j] + mortInt[i][j] + charDon[i][j];
                
                // STATE
                switch (filingState[i].toUpperCase()) {
                    case "NJ" -> {
                        itemDedState[i][j] = 0;
                    } 
                
                    case "MD" -> {
                        itemDedState[i][j] = 0;
                    }
                }
            }
        }
        
        Utility.ArrayMath.sumArrays2(new int[]{iters,years},mortInt,charDon,slpDed);
    }
    
    public static void stdDedCalc() {
        TaxDict.Federal.Deductions.Standard dedFed = taxes.federal.deductions.standard;
                
        for (int i = 0; i < iters; i++) {
            for (int j = 0; j < years; j++) {
                // FEDERAL
                stdDedFed[i][j] = (dedFed.maxFed * numInd) / iters;
                
                // STATE
                switch (filingState[i].toUpperCase()) {
                    case "NJ" -> {
                        stdDedState[i][j] = 0;
                    } 
                
                    case "MD" -> {
                        TaxDict.State.Args.Deductions.Standard dedState = taxes.state.md.deductions.standard;

                        stdDedState[i][j] = (int) (dedState.basePerc * income[i][j]);

                        if (stdDedState[i][j] < dedState.stdDedMin / iters) {
                            stdDedState[i][j] = (int) (dedState.stdDedMin / iters);
                        } else if (stdDedState[i][j] > dedState.stdDedMax / iters) {
                            stdDedState[i][j] = (int) (dedState.stdDedMax / iters);
                        }  
                    }
                    
                    case "AK", "FL", "NV", "NH", "SD", "TN", "TX", "WA", "WY" -> {
                        stdDedState[i][j] = 0;
                    }
                }   
            }
        }
    }
    
    public static void exemptCalc() {
        TaxDict.Federal.Exemptions fedExempt = taxes.federal.exemptions;
        
        for (int i = 0; i < iters; i++) {
            for (int j = 0; j < years; j++) {
                // FEDERAL
                exemptFed[i][j] = 0;
                
                // STATE
                TaxDict.State.Args.Filing persExempt;
                TaxDict.State.Args.Filing childExempt;
                
                switch (filingState[i].toUpperCase()) {
                    case "NJ" -> {
                        switch (filingType.toUpperCase()) {
                            case "JOINT" ->  {
                                persExempt = taxes.state.nj.exemptions.persExempt.joint;
                                childExempt = taxes.state.nj.exemptions.childExempt.joint;
                            }
                            case "SEPARATE" -> {
                                persExempt = taxes.state.nj.exemptions.persExempt.separate;
                                childExempt = taxes.state.nj.exemptions.childExempt.separate;
                            }
                            case "SINGLE" -> {
                                persExempt = taxes.state.nj.exemptions.persExempt.single;
                                childExempt = taxes.state.nj.exemptions.childExempt.single;
                            }
                            default -> { // Assume Single
                                persExempt = taxes.state.nj.exemptions.persExempt.single;
                                childExempt = taxes.state.nj.exemptions.childExempt.single;
                            }
                        }                        
                                
                        for (int k = 0; k < persExempt.bracketMax.length; k++) {                            
                            if (income[i][j] < persExempt.bracketMax[k]) {
                                persExemptState[i][j] = persExempt.bracketAmt[k];                                
                                break;
                            }
                        }
                        
                        for (int[] childAge : childAges) {
                            if (childAge[j] > 0 && childAge[j] <= maxChildYr) {
                                for (int k = 0; k < childExempt.bracketMax.length; k++) {
                                    if (income[i][j] < childExempt.bracketMax[k]) {
                                        childExemptState[i][j] += childExempt.bracketAmt[k] / iters;
                                        break;
                                    }
                                }
                            }
                        }
                    }
                    
                    case "MD" -> {
                        switch (filingType.toUpperCase()) {
                            case "JOINT" ->  {
                                persExempt = taxes.state.md.exemptions.persExempt.joint;
                                childExempt = taxes.state.md.exemptions.childExempt.joint;
                            }
                            case "SEPARATE" -> {
                                persExempt = taxes.state.md.exemptions.persExempt.separate;
                                childExempt = taxes.state.md.exemptions.childExempt.separate;
                            }
                            case "SINGLE" -> {
                                persExempt = taxes.state.md.exemptions.persExempt.single;
                                childExempt = taxes.state.md.exemptions.childExempt.single;
                            }
                            default -> { // Assume Single
                                persExempt = taxes.state.md.exemptions.persExempt.single;
                                childExempt = taxes.state.md.exemptions.childExempt.single;
                            }
                        }
                        
                        for (int k = 0; k < persExempt.bracketMax.length; k++) {
                            if (income[i][j] < persExempt.bracketMax[k]) {
                                persExemptState[i][j] = persExempt.bracketAmt[k];
                                break;
                            }
                        }
                        
                        for (int[] childAge : childAges) {
                            if (childAge[j] > 0 && childAge[j] <= maxChildYr) {
                                for (int k = 0; k < childExempt.bracketMax.length; k++) {
                                    if (income[i][j] < childExempt.bracketMax[k]) {
                                        childExemptState[i][j] += childExempt.bracketAmt[k] / iters;
                                        break;
                                    }
                                }
                            }
                        }
                    }
                    
                    case "AK", "FL", "NV", "NH", "SD", "TN", "TX", "WA", "WY" -> {
                        persExemptState[i][j] = 0;
                        childExemptState[i][j] = 0;
                    }
                }
            }
        }
    }
    
    public static void grossEarnCalc() {
        for (int i = 0; i < iters; i++) {
            for (int j = 0; j < years; j++) {
                // FEDERAL
                grossIncomeFed[i][j] = income[i][j] - (vars.benefits.retirement.traditional.contribution[i][j] + 
                                                        healthDed[i][j] + 
                                                        exemptFed[i][j]);
                        
                if (itemDedFed[i][j] > stdDedFed[i][j]) {
                    grossIncomeFed[i][j] -= itemDedFed[i][j];
                } else {
                    grossIncomeFed[i][j] -= stdDedFed[i][j];
                }
                
                // STATE
                switch (filingState[i].toUpperCase()) {
                    case "NJ","CA" -> {
                        grossIncomeState[i][j] = income[i][j] - (vars.benefits.retirement.traditional.contribution[i][j] + 
                                                                    persExemptState[i][j] + childExemptState[i][j]);
                    }
                    
                    case "AK", "FL", "NV", "NH", "SD", "TN", "TX", "WA", "WY" -> {
                        grossIncomeState[i][j] = income[i][j];
                    }
                    
                    default -> {
                        grossIncomeState[i][j] = income[i][j] - (vars.benefits.retirement.traditional.contribution[i][j] +
                                                                    healthDed[i][j] + 
                                                                    persExemptState[i][j] + childExemptState[i][j]);
                    }
                }
                
                switch (filingState[i].toUpperCase()) {
                    case "AK", "FL", "NV", "NH", "SD", "TN", "TX", "WA", "WY" -> {}
                    
                    default -> {
                        if (itemDedState[i][j] > stdDedState[i][j]) {
                            grossIncomeState[i][j] -= itemDedState[i][j];
                        } else {
                            grossIncomeState[i][j] -= stdDedState[i][j];
                        }
                    }
                }
            }
        }
    }
    
    public static void slTaxCalc() {
        TaxDict.State.Args.Filing state;
        TaxDict.State.Args.LocalTax local;
        Vars.Expenses.Housing.House house = vars.expenses.housing.house;
        
        saltTaxes = new int[iters][years];
        
        for (int i = 0; i < iters; i++) {
            switch (filingState[i].toUpperCase()) {
                case "NJ" -> {
                    switch (filingType.toUpperCase()) {
                        case "JOINT" ->     state = taxes.state.nj.state.joint;
                        case "SEPARATE" ->  state = taxes.state.nj.state.separate;
                        case "SINGLE" ->    state = taxes.state.nj.state.single;
                        default ->          state = taxes.state.nj.state.single; // Assume Single
                    }

                    local = taxes.state.nj.local;
                }

                case "MD" -> {
                    switch (filingType.toUpperCase()) {
                        case "JOINT" ->     state = taxes.state.md.state.joint;
                        case "SEPARATE" ->  state = taxes.state.md.state.separate;
                        case "SINGLE" ->    state = taxes.state.md.state.single;
                        default ->          state = taxes.state.md.state.single; // Assume Single
                    }

                    local = taxes.state.md.local;
                }

                case "AK", "FL", "NV", "NH", "SD", "TN", "TX", "WA", "WY" -> {
                    state = taxes.state.none.state.none;
                    local = taxes.state.none.local;
                }

                default -> {
                    state = taxes.state.none.state.none;
                    local = taxes.state.none.local;
                }
            }
            
            for (int j = 0; j < years; j++) {
                int maxBracket = 0;
                int minBracket;
                double rateBracket;
                for (int k = 0; k < state.bracketMax.length; k++) {
                    minBracket = maxBracket;
                    maxBracket = state.bracketMax[k];
                    rateBracket = state.bracketPerc[k];
                    
                    if (grossIncomeState[i][j] > maxBracket) {
                        stateTax[i][j] += (int) ((maxBracket - minBracket) * rateBracket);
                    } else if (grossIncomeState[i][j] > minBracket) {
                        stateTax[i][j] += (int) ((grossIncomeState[i][j] - minBracket) * rateBracket);
                    }
                }
                
                localTax[i][j] = (int) (grossIncomeState[i][j] * local.localPerc);
                propTax[i][j] = (int) (house.houseWth[j] * house.propTax);
                
                saltTaxes[i][j] += stateTax[i][j] + localTax[i][j] + propTax[i][j];
            }
        }
    }
    
    public static void fedTaxCalc() {
        TaxDict.Federal.FederalTax.Filing federal;
        TaxDict.Federal.Fica.Filing medicare;
        TaxDict.Federal.Fica.Filing socialSecurity;
        
        switch (filingType.toUpperCase()) {
            case "JOINT" -> {    
                federal = taxes.federal.federal.joint;
                medicare = taxes.federal.fica.med.joint;
                socialSecurity = taxes.federal.fica.ss.joint;
            }
            case "SEPARATE" -> { 
                federal = taxes.federal.federal.separate;
                medicare = taxes.federal.fica.med.separate;
                socialSecurity = taxes.federal.fica.ss.separate;
            }
            case "SINGLE" -> {   
                federal = taxes.federal.federal.single;
                medicare = taxes.federal.fica.med.single;
                socialSecurity = taxes.federal.fica.ss.single;
            }
            default -> { // Assume Single        
                federal = taxes.federal.federal.single; 
                medicare = taxes.federal.fica.med.single;
                socialSecurity = taxes.federal.fica.ss.single;
            }
        }
        
        for (int i = 0; i < iters; i++) {
            for (int j = 0; j < years; j++) {                
                // Federal Tax
                int maxBracket = 0;
                int minBracket;
                double rateBracket;
                for (int k = 0; k < federal.bracketMax.length; k++) {
                    minBracket = maxBracket;
                    maxBracket = federal.bracketMax[k];
                    rateBracket = federal.bracketPerc[k];
                    
                    if (grossIncomeFed[i][j] > maxBracket) {
                        fedTax[i][j] += (int) ((maxBracket - minBracket) * rateBracket);
                    } else if (grossIncomeFed[i][j] > minBracket) {
                        fedTax[i][j] += (int) ((grossIncomeFed[i][j] - minBracket) * rateBracket);
                    }
                }
                
                // SS Tax
                if (grossIncomeFed[i][j] < socialSecurity.maxSal) {
                    ficaTax[i][j] += (int) (grossIncomeFed[i][j] * socialSecurity.rate);
                } else {
                    ficaTax[i][j] += (int) (socialSecurity.maxSal * socialSecurity.rate);
                }
                
                // Medicare Tax
                if (grossIncomeFed[i][j] < medicare.maxSal) {
                    ficaTax[i][j] += (int) (grossIncomeFed[i][j] * medicare.rate);
                } else {
                    ficaTax[i][j] += (int) (medicare.maxSal * medicare.rate);
                    ficaTax[i][j] += (int) ((grossIncomeFed[i][j] - medicare.maxSal) * medicare.addRate);
                }
            }
        }
    }
    
    public static void netIncCalc() {
        Vars.Benefits.Retirement ret = vars.benefits.retirement;
        
        for (int i = 0; i < iters; i++) {
            for (int j = 0; j < years; j++) {
                totalTaxes[j] += fedTax[i][j] + ficaTax[i][j] + saltTaxes[i][j];
                totalDeducted[j] += ret.traditional.contribution[i][j] +
                                    healthDed[i][j];
                totalWithheld[j] += ret.roth.contribution[i][j] +
                                    healthBen[i][j];
                
                netIncome[j] += vars.salary.income[i][j];
                netTradRet[j] += ret.traditional.contribution[i][j] + ret.match.contribution[i][j];
                netRothRet[j] += ret.roth.contribution[i][j];
            }
        }
        
        for (int j = 0; j < years; j++) {
            netIncome[j] -= totalTaxes[j];
            netCash[j] = netIncome[j] - totalDeducted[j] - totalWithheld[j];
        }        
    }
}