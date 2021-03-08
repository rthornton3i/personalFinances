package com.personalfinances;

public class Reader {
    // Public Variables
    static int years;
    
    static Vars vars;
    
    public Reader(Vars vars) {
        this.vars = vars;
        
        years = vars.base.years;
    }
        
    public void run() {
        readInputs();
    }
    
    public void readInputs() {
        String[] header = {"header1","header2"};
        
        String filename = "Inputs.xlsx";
        
        Utility.CSV.csvRead(header,filename);
    }
}
