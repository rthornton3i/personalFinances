package com.personalfinances;

public class Writer {
    // Public Variables
    static int years;
    
    static Vars vars;
    
    public Writer(Vars vars) {
        this.vars = vars;
        
        years = vars.base.years;
    }
        
    public void run() {
        writeExpenses();
        writeSavings(vars.savings.savings,"Savings.csv");
        writeSavings(vars.savings.contributions,"Contributions.csv");
    }
    
    public void writeExpenses() {
        String[][] lines = new String[years+1][18];
        
        int j = 0;
        lines[0][j] = "YEARS"; j+=1;
        lines[0][j] = "Gross Income"; j+=1;
        lines[0][j] = "Net Income"; j+=1;
        lines[0][j] = "Net Cash"; j+=1;
        lines[0][j] = "Net Savings"; j+=1;
        lines[0][j] = "House"; j+=1;
        lines[0][j] = "Car"; j+=1;
        lines[0][j] = "Food"; j+=1;
        lines[0][j] = "Entertainment"; j+=1;
        lines[0][j] = "Personal Care"; j+=1;
        lines[0][j] = "Healthcare"; j+=1;
        lines[0][j] = "Pet"; j+=1;
        lines[0][j] = "Holiday"; j+=1;
        lines[0][j] = "Education"; j+=1;
        lines[0][j] = "Vacation"; j+=1;
        lines[0][j] = "Charity"; j+=1;
        lines[0][j] = "Major"; j+=1;
        lines[0][j] = "Random"; j+=1;
        
        int k = 0;
        for (int i = 0; i < years; i++) {
            j = 0;
            lines[i+1][j] = String.valueOf(i); j+=1;
            lines[i+1][j] = String.valueOf(vars.salary.grossIncome[i]); j+=1;
            lines[i+1][j] = String.valueOf(vars.taxes.netIncome[i]); j+=1;
            lines[i+1][j] = String.valueOf(vars.taxes.netCash[i]); j+=1;
            lines[i+1][j] = String.valueOf(vars.taxes.netCash[i] - vars.expenses.totalExp[i]); j+=1;
            lines[i+1][j] = String.valueOf(vars.expenses.totalExpenses[k][i]); j+=1; k+=1; // House
            lines[i+1][j] = String.valueOf(vars.expenses.totalExpenses[k][i]); j+=1; k+=1; // Car
            lines[i+1][j] = String.valueOf(vars.expenses.totalExpenses[k][i]); j+=1; k+=1; // Food
            lines[i+1][j] = String.valueOf(vars.expenses.totalExpenses[k][i]); j+=1; k+=1; // Entertainment
            lines[i+1][j] = String.valueOf(vars.expenses.totalExpenses[k][i]); j+=1; k+=1; // Personal Care
            lines[i+1][j] = String.valueOf(vars.expenses.totalExpenses[k][i]); j+=1; k+=1; // Health
            lines[i+1][j] = String.valueOf(vars.expenses.totalExpenses[k][i]); j+=1; k+=1; // Pet
            lines[i+1][j] = String.valueOf(vars.expenses.totalExpenses[k][i]); j+=1; k+=1; // Holiday
            lines[i+1][j] = String.valueOf(vars.expenses.totalExpenses[k][i]); j+=1; k+=1; // Education
            lines[i+1][j] = String.valueOf(vars.expenses.totalExpenses[k][i]); j+=1; k+=1; // Vacation
            lines[i+1][j] = String.valueOf(vars.expenses.totalExpenses[k][i]); j+=1; k+=1; // Charity
            lines[i+1][j] = String.valueOf(vars.expenses.totalExpenses[k][i]); j+=1; k+=1; // Major
            lines[i+1][j] = String.valueOf(vars.expenses.totalExpenses[k][i]); j+=1; k=0; // Random
        }
        
        Utility.CSV.csvWrite(lines,"Expenses.csv");
    }
    
    public void writeSavings(int[][] savings, String filename) {
        String[][] lines = new String[years+1][12];
        
        int j = 0;
        lines[0][j] = "YEARS"; j+=1;
        lines[0][j] = "High Dividend"; j+=1;
        lines[0][j] = "Low Volatility"; j+=1;
        lines[0][j] = "Value/Growth"; j+=1;
        lines[0][j] = "Sector Indexes"; j+=1;
        lines[0][j] = "Swing/Day"; j+=1;
        lines[0][j] = "Roth Ret"; j+=1;
        lines[0][j] = "Trad Ret"; j+=1;
        lines[0][j] = "College 529"; j+=1;
        lines[0][j] = "Long-Term Savings"; j+=1;
        lines[0][j] = "Short-Term Savings"; j+=1;
        lines[0][j] = "Spending"; j+=1;
        
        int k = 0;
        for (int i = 0; i < years; i++) {
            j = 0;
            lines[i+1][j] = String.valueOf(i); j+=1;
            lines[i+1][j] = String.valueOf(savings[k][i]); j+=1; k+=1; // hiDiv
            lines[i+1][j] = String.valueOf(savings[k][i]); j+=1; k+=1; // lowVol
            lines[i+1][j] = String.valueOf(savings[k][i]); j+=1; k+=1; // valueGrowth
            lines[i+1][j] = String.valueOf(savings[k][i]); j+=1; k+=1; // sectorInd
            lines[i+1][j] = String.valueOf(savings[k][i]); j+=1; k+=1; // swingDay
            lines[i+1][j] = String.valueOf(savings[k][i]); j+=1; k+=1; // retRoth401
            lines[i+1][j] = String.valueOf(savings[k][i]); j+=1; k+=1; // retTrad401
            lines[i+1][j] = String.valueOf(savings[k][i]); j+=1; k+=1; // col529
            lines[i+1][j] = String.valueOf(savings[k][i]); j+=1; k+=1; // longTerm
            lines[i+1][j] = String.valueOf(savings[k][i]); j+=1; k+=1; // shortTerm
            lines[i+1][j] = String.valueOf(savings[k][i]); j+=1; k=0;  // spend
        }
        
        Utility.CSV.csvWrite(lines,filename);
    }
}
