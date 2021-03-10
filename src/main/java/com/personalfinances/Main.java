package com.personalfinances;

public class Main {

    public static void main(String[] args) { //throws InterruptedException {
//        App.start();

        long startTime = System.nanoTime();
        
        Vars vars = new Vars();
        double[][] totalExpenses = new double[vars.expenses.numExpenses][vars.base.years];
        double[][] totalSavings = new double[vars.allocations.numAccounts][vars.base.years];
        
        for (int i = 0; i < vars.base.loops; i++) {
            vars = new Vars();
            TaxDict taxDict = new TaxDict();

//            Reader reader = new Reader(vars);
//            reader.run();

            Setup setup = new Setup(vars);
            vars = setup.run();

            Loans loans = new Loans(vars);
            vars = loans.run();

            Expenses expenses = new Expenses(vars);
            vars = expenses.run();

            Taxes taxes = new Taxes(vars, taxDict);
            vars = taxes.run();

            Savings savings = new Savings(vars);
            vars = savings.run();
            
            totalExpenses = Utility.ArrayMath.sumArrays2D(new int[]{vars.expenses.numExpenses,vars.base.years}, 
                                                         totalExpenses, Utility.Conversion.int2double2(new int[]{vars.expenses.numExpenses,vars.base.years},vars.expenses.totalExpenses));
            
            totalSavings = Utility.ArrayMath.sumArrays2D(new int[]{vars.allocations.numAccounts,vars.base.years}, 
                                                         totalSavings, Utility.Conversion.int2double2(new int[]{vars.allocations.numAccounts,vars.base.years},vars.savings.savings));
        }
        
        vars.expenses.totalExpenses = Utility.Conversion.double2int2(new int[]{vars.expenses.numExpenses,vars.base.years}, Utility.ArrayMath.avgArrays2D(new int[]{vars.expenses.numExpenses,vars.base.years,vars.base.loops}, totalExpenses));
        vars.savings.savings        = Utility.Conversion.double2int2(new int[]{vars.allocations.numAccounts,vars.base.years}, Utility.ArrayMath.avgArrays2D(new int[]{vars.allocations.numAccounts,vars.base.years,vars.base.loops}, totalSavings));
        
        System.out.println("Net Worth: " + Utility.ArrayMath.sumArray2(vars.savings.savings,1)[vars.base.years-1]);
        
//        Writer writer = new Writer(vars);
//        writer.run();
                
//        class.start();
//        class.join();
        
        long stopTime = System.nanoTime();
        System.out.println("Elapsed time was " + (double)((stopTime - startTime) / 1e9) + " seconds.");
    }
}