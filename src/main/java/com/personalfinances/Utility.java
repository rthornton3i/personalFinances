package com.personalfinances;

import java.lang.Math;
import java.util.Random;

import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.BufferedReader;  
import java.io.FileReader;  
import java.nio.charset.StandardCharsets;

public class Utility {
    
    public static class Generator {
        
        public static double triRand(double a, double b, double c) {
            double U = Math.random();

            if (U < (b - a) / (c - a)) {
              return a + Math.sqrt(U * (b - a) * (c - a));
            } else {
              return c - Math.sqrt(U * (c - b) * (c - a));
            }
        }
        
        public static double normalRand(double mean, double stdDev) {
            Random rand = new Random();
            double r;
            
            r = rand.nextGaussian();
            r *= stdDev;
            r += mean;
            
            return r;
        }
        
        public static int[] rangeRand(int[] range, int len, String type) {
            int[] rng = new int[len];
            
            for (int i = 0; i < len; i++) {
                switch (type.toUpperCase()) {
                    case "UNIFORM" -> {
                        rng[i] = (int) Math.round((Math.random() * (range[1] - range[0])) + range[0]);
                    }
                    case "NORMAL" -> {
                        double mean = (range[0] + range[1]) / 2;
                        double std = (range[1] - mean) / 3;
                        rng[i] = (int) Math.round((normalRand(mean,std) * (range[1] - range[0])) + range[0]);
                    }
                }
            }
            
            return rng;
        }
    }
    
    public static class Conversion {
        
        public static double[][] int2double2(int[] numel, int[][] arr) {
            double[][] int2double = new double[numel[0]][numel[1]];

            for (int i = 0; i < numel[0]; i++) {
                for (int j = 0; j < numel[1]; j++) {
                    int2double[i][j] += (double) arr[i][j];
                }
            }

            return int2double;
        }

        public static int[][] double2int2(int[] numel, double[][] arr) {
            int[][] int2double = new int[numel[0]][numel[1]];

            for (int i = 0; i < numel[0]; i++) {
                for (int j = 0; j < numel[1]; j++) {
                    int2double[i][j] += (int) arr[i][j];
                }
            }

            return int2double;
        }
    }
    
    public static class ArrayMath {
        
        public static int sumArray(int[] arr) {
            int sumArray = 0;

            for (int i = 0; i < arr.length; i++) {
                sumArray += arr[i];
            }

            return sumArray;
        }

        public static int[] sumArray2(int[][] arr, int axis) {
            if (axis == 0) {
            } else if (axis == 1) {
                int[] sumArray2 = new int[arr[0].length];

                for (int j = 0; j < arr[0].length; j++) {
                    for (int i = 0; i < arr.length; i++) {
                        sumArray2[j] += arr[i][j];
                    }
                }
                return sumArray2;
            } 
            return null;
        }
        
        public static double[] sumArray2D(double[][] arr, int axis) {
            if (axis == 0) {
            } else if (axis == 1) {
                double[] sumArray2 = new double[arr[0].length];

                for (int j = 0; j < arr[0].length; j++) {
                    for (int i = 0; i < arr.length; i++) {
                        sumArray2[j] += arr[i][j];
                    }
                }
                return sumArray2;
            } 
            return null;
        }

        public static int[] sumArrays(int numel, int[] ... arrs) {
            int[] sumArrays = new int[numel];

            for (int[] arr : arrs) {            
                for (int i = 0; i < numel; i++) {
                    sumArrays[i] += arr[i];
                }
            }

            return sumArrays;
        }

        public static int[][] sumArrays2(int[] numel, int[][] ... arrs) {
            int[][] sumArrays = new int[numel[0]][numel[1]];

            for (int[][] arr : arrs) {  
                for (int i = 0; i < numel[0]; i++) {
                    for (int j = 0; j < numel[1]; j++) {
                        sumArrays[i][j] += arr[i][j];
                    }
                }
            }

            return sumArrays;
        }

        public static double[][] sumArrays2D(int[] numel, double[][] ... arrs) {
            double[][] sumArrays = new double[numel[0]][numel[1]];

            for (double[][] arr : arrs) {  
                for (int i = 0; i < numel[0]; i++) {
                    for (int j = 0; j < numel[1]; j++) {
                        sumArrays[i][j] += arr[i][j];
                    }
                }
            }

            return sumArrays;
        }

        public static double[][] multArrays2(int[] numel, double[][] ... arrs) {
            double[][] multArrays = new double[numel[0]][numel[1]];

            boolean isFirstArr = true;
            for (double[][] arr : arrs) {  
                for (int i = 0; i < numel[0]; i++) {
                    for (int j = 0; j < numel[1]; j++) {
                        if (isFirstArr) {
                            multArrays[i][j] = arr[i][j];
                        } else {
                            multArrays[i][j] *= arr[i][j];
                        }                        
                    }
                }

                isFirstArr = false;
            }

            return multArrays;
        }
        
        public static int[][] avgArrays2(int[] numel, int[][] arr) {
            int[][] avgArrays = new int[numel[0]][numel[1]];
            
            for (int i = 0; i < avgArrays.length; i++) {
                for (int j = 0; j < avgArrays[0].length; j++) {
                    avgArrays[i][j] = arr[i][j] / numel[2];
                }
            }

            return avgArrays;
        }
        
        public static double[][] avgArrays2D(int[] numel, double[][] arr) {
            double[][] avgArrays = new double[numel[0]][numel[1]];
            
            for (int i = 0; i < avgArrays.length; i++) {
                for (int j = 0; j < avgArrays[0].length; j++) {
                    avgArrays[i][j] = arr[i][j] / numel[2];
                }
            }

            return avgArrays;
        }
    }
    
    public static class CSV {
        
        public static void csvWrite(String[][] lines, String filename) {
            try (PrintWriter writer = new PrintWriter(new File(filename))) {
                StringBuilder sb = new StringBuilder();
                
                for (int i = 0; i < lines.length; i++) {
                    for (int j = 0; j < lines[i].length; j++) {
                        sb.append(lines[i][j]);
                        if (j == lines[i].length - 1) {
                            sb.append('\n');
                        } else {
                            sb.append(',');
                        }
                    }
                }
                
                writer.write(sb.toString());
                
            } catch (IOException e) {
                System.out.println(e.getMessage());
            }
        }
        
        public static void csvRead(String[] header, String filename) {
            String line = null;
            try (BufferedReader reader = new BufferedReader(new FileReader(filename,StandardCharsets.UTF_8))) {  
                while ((line = reader.readLine()) != null) {  
                    String[] data = line.split(",");
                    System.out.println(data[0]);
//                    for (int i = 0; i < lines.length; i++) {
//                        for (int j = 0; j < lines[i].length; j++) {
//                            sb.append(lines[i][j]);
//                            if (j == lines[i].length - 1) {
//                                sb.append('\n');
//                            } else {
//                                sb.append(',');
//                            }
//                        }
//                    }
                }
                
            } catch (IOException e) {
                System.out.println(e.getMessage());
            }
        }
    }
}
