---
title: "R Introduction Tutorial 1 (BT5126)"
author: "Yuening"
header-includes:
- \usepackage{setspace}
- \doublespacing
output:
  html_document:
    theme: readable
    toc: yes
    toc_depth: 3
    toc_float: true
    highlight: tango
fontsize: 16pt
---

```{r setup, include=FALSE}
knitr::opts_chunk$set(echo = TRUE)
```

## R Data Types

### Scalars

```{r}
a <- 1 # object names cannot start with numbers
a + 1
b <- 2
a + b
```

### Vectors 

```{r}
num.vector <- c(1,2,3,4) # numeric vectors
num.vector + 1
num.vector * 2
char.vector <- c("a","b","c","d") # character vectors
```

```{r}
num.vector[0]
num.vector[c(1,3,4)]
num.vector[2:4]
num.vector[-2] # remove second element
```

```{r}
class(num.vector)
class(char.vector)
```

```{r}
# assigning values to vectors
char.vector[4] <- "fourth letter"
char.vector
```


### Dataframes

```{r}
df <- data.frame(num.vector, char.vector, new.vector = 5:8)
df
```

```{r}
## Subsetting Dataframes
# left of comma rows
# right of comma columns
df[2,2]
df[c(1,2), 2]
df[1:2, ]
```

```{r}
# subsetting using $
df$num.vector
df$char.vector[1:2]
```

```{r}
# assigning values to dataframe
df[2, "num.vector"] <- 10
df
df$one.more.vector <- c("b","l","a","h")
df
```

```{r}
# summarizing dataframes
class(df)
str(df)
summary(df)
names(df)
nrow(df) 
ncol(df)
dim(df)
```

## Logical Statements and Operators

```{r}

1 > 2

3 == 0 # check equality

4 <= 6

TRUE + TRUE + FALSE

(1 > 2) + (3==0)

## more operators

2 != 3 ## not

2 >= 2

2==2 & 3>1 # and

2==1 & 3>1

2!=2 | 3>1 # or

2 %in% 1:4 # subset of

c(2,5) %in% 1:4

```

```{r}
missing.vector <- c(1,NA,3,NA)

is.na(missing.vector)

!is.na(missing.vector)

missing.vector[!is.na(missing.vector)]
```

```{r}
num.vector
num.vector > 3

num.vector[c(FALSE, FALSE, FALSE, TRUE)]

num.vector[num.vector > 3]

```

```{r}

char.vector == "b"

char.vector[char.vector == "b"]

df

df[char.vector == "b", ]

```

## for loops 

```{r}
for (i in 1:10) {
  print(i)
}
```

## conditionals

```{r}
x = 10
if (x > 5){
  print("x is more than 5.")
} else if (x < 0) {
  print("x is less than 0.")
} else {
  print("x is something else.")
}
```


## R Functions

```{r}
?class # help documents

?rnorm
```

```{r}

rnorm(n = 10, mean = 10, sd = 1) #random numbers from a normal (Gaussian) distribution
rnorm(10,10, 1)

norm <- rnorm(10000, mean = 10, sd  = 1)

plot(norm)
mean(norm)
sd(norm)

```

```{r}
double <- function(x){
  return(2*x) 
}

double(10)

```

## Let's Try Working with a Real Dataset!

The worksheet Base Data in the Excel file Bank Credit Risk Data provides information about 425 bank customers who had applied for loans. Each of the column is defined as follows: 

- `Loan Purpose` : Type of purpose for the loan applied
- `Checking` : Checking account balance
- `Savings` :  Savings account balance
- `Months Customer`: Number of months has been a customer of the bank
- `Months Employed`: Number of months in employment
- `Gender`: Gender
- `Marital Status`: Marital status 
- `Age`: Age in years
- `Housing`: Housing type
- `Years`: Number of years at current residence
- `Job`: Job type
- `Credit Risk`: Credit-risk classification by the bank

```{r}
library(dplyr) 
library(tidyr)
library(readxl)
library(RColorBrewer)
```


```{r }

getwd()
setwd("/Users/yanyuening/Downloads/Tutorial1") # set working directory

library(readxl)
credit <- read_excel("CreditRiskData.xlsx", 
                               sheet = "Base Data", skip = 2) 

# sheet argument is specified because the excel file has multiple sheets
# skip = 2 skips the first 2 rows of the excel file 
```

```{r}
# useful summary functions
summary(credit)
str(credit)
head(credit)
#head(credit, 10)
tail(credit)
glimpse(credit) #str
```

### Factor Variables

```{r}

# calling for a variable `Credit Risk` in dataframe `credit`
credit$`Credit Risk`
# calling first 20 observations (rows) and 2nd to 5th variables (cols)
credit[1:20, c(2:5)]

# from 'str(credit)', note that variable 'credit$'Credit Risk' is data type of `chr`, character. We could also use:
is.factor(credit$`Credit Risk`)
# converting a string variable to factor (binary). Additional label line.
credit$credit_risk = as.factor(credit$`Credit Risk`)
credit$credit_risk
# similarly, convert a string variable 'credit$`Job`' to a ordered factor variable (categorical); order is manually specified
credit$job = factor(credit$Job, levels = c("Unemployed", "Unskilled", "Skilled", "Management"), ordered = TRUE)
# show contingency table for 2 variables (meaningful only for categorical variables or factors).
table(credit$credit_risk, credit$job) 

# Remarks:
# A good practice about dealing with data: keep original data immutable and make copy of it. Create new ones (dataframe/variables) if you want to change sth. 
```

### Basic Data Manipulations with `dplyr` 

```{r}

## `dplyr`` package provides a function for each basic verb of data manipulation:
# filter() to select cases based on their values.
# slice() to select cases based on row index
# arrange() to reorder the cases.
# select() and rename() to select variables based on their names.
# mutate() and transmute() to add new variables that are functions of existing variables.
# summarise() to condense multiple values to a single value.
# sample_n() and sample_frac() to take random samples.

## how many loan applicants are single?
# extract `Marital Status` column (i.e. variable) as a tibble (variant of dataframe) with one column
ms <- credit %>% select(`Marital Status`)
# filter, or select, rows (i.e. observation) whose value is "Single"
single <- ms %>% filter(`Marital Status` == "Single")
# count number of "single"
nrow(single)
# equivalently, 
ms %>% filter(`Marital Status`=="Single") %>% count()
# count all values 
ms %>% count(`Marital Status`)
# or equivalently
ms %>% group_by (`Marital Status`) %>% tally()

## what is the marital status of the 40th applicant?
slice(ms, 40)
# or equivalently,
ms[40,]

## what is the difference of `Savings` of the 46th and 27th applicant
slice(credit, 46)[, "Savings"] - slice(credit, 27)[,"Savings"]
# or "equivalently", 
slice(credit, 46)$Savings - slice(credit, 27)$Savings

```

```{r}

## create a new variable in dataframe `Total Account` = `Checking` + `Saving`
credit$`Total Account` <- credit$Checking + credit$Savings
# on top of `Total Account`, create a categorical variable `Account Level` such that 
# `Account Level` = "low" if `Total Account <= 600` 
# `Account Level` = "medium" if   600 < `Total Account < 1200`
# `Account Level` = "high" if `Total Account >= 1200`
credit$`Account Level`[credit$`Total Account` <= 600] = "low"
credit$`Account Level`[credit$`Total Account` > 600 & credit$`Total Account` < 1200] = "medium"
credit$`Account Level`[credit$`Total Account` >= 1200] = "high"
# produce a frequency table about `Account level`
credit %>% count(`Account Level`)

```

### Exporting Data

```{r}

## export the current dataframe `credit` to a CSV file for observations whose `Account Level` == "high"
write.csv(filter(credit, `Account Level` == "high"), file = "CreditRisk_high.csv", row.names = FALSE)

```

### Summary Statistics

```{r}

## Summary Statistics Table: Long-Wide Data Transformation ##
# a quick summary of statistics for selected variables. Be familiar with the use of ``piping'' %>%.  
credit.sum = credit %>%
  select(Checking, Savings, `Months Customer`, `Months Employed`, Age) %>%      # select variables to summarise
  summarise_each(list(min = min, 
                      median = median, 
                      max = max,
                      mean = mean, 
                      var = var,
                      sd = sd))
# display the summary statistics 
print(credit.sum)
# display the dimension of an object in R and you shall see 'mroz.sum' is in weird shape, i.e. one long row with values of statistics in columns.
dim(credit.sum)

# Remarks:
# credit.sum is a data frame in weird shape. (However, please note that the original data set 'credit' is in normal wide form.)
# firstly use gather function to collect values of statistics into rows. 
# now credit.sum is in "long-form", then use spread function in tidyr to change it to "wide-form". In many occassions, you need to
# wrangle the original data set into different forms to perform different analyses. I recommend you run line by line to see what changes have been made.
credit.sumstats = credit.sum %>% gather(stats, value) %>%
  separate(stats, into = c("Var", "Stats"), sep = "_") %>%
  spread(Stats, value) %>%
  select(Var, min, median, max, mean, var, sd) # reorder columns
# print an object in R
print(credit.sumstats) 
dim(credit.sumstats)


```

### Simple Data Visualization 

```{r}

## Scatterplot between two variables
# a simple scatter plot between two variables
p1 = plot(credit$Age, credit$Savings, main="Simple Scatterplot of Savings vs. Age", 
     xlab="age", ylab="saving")

# open a PDF device to produce a figure in PDF
pdf("plot-AgeSavings.pdf", width=4, height=6)
mar <- par("mar")
mar = c(4,4,2.5,2)
par(mar = mar)
plot(credit$Age, credit$Savings, main="Simple Scatterplot of Savings vs. Age", 
     xlab="age", ylab="saving")
dev.off()

## Grouped bar chart for frequency comparison

# compare the frequencies of loan purposes, by gender
byloans_male = credit %>% filter(Gender == "M") %>% group_by(`Loan Purpose`) %>% summarise(male = n()) 
byloans_female = credit %>% filter(Gender == "F") %>% group_by(`Loan Purpose`) %>% summarise(female = n()) 
byloans_gender = merge(byloans_male, byloans_female, by = "Loan Purpose", all = TRUE)
print(byloans_gender)

# extract gender counts as a pure numeric matrix
barmat = as.matrix(byloans_gender[,2:3])
# let's pick "Spectral" color palette provided in RColorBrewer package. Color sampling numbers depends on unique levels of `Loan Purpose`
# see all avaiable color palettes:
display.brewer.all()
# reference on R's color options: http://www.stat.columbia.edu/~tzheng/files/Rcolor.pdf
bar_colors = brewer.pal(n=length(unique(byloans_gender$`Loan Purpose`)), name = 'Spectral')
p2 = barplot(barmat, names.arg = c("Male", "Female"), col = bar_colors, 
             beside = TRUE, main = "Loan Purpose by Gender", ylim = c(0, 120))
legend("topright", byloans_gender$`Loan Purpose`, cex = 0.7, fill = bar_colors)

# produce a figure in PDF
pdf("plot-LoanbyGender.pdf", width=6, height=4)
mar <- par("mar")
mar = c(4,4,2.5,2)
par(mar = mar) #Retrieves the current margin settings for the plot
barplot(barmat, names.arg = c("Male", "Female"), col = bar_colors, 
             beside = TRUE, main = "Loan Purpose by Gender", ylim = c(0, 120))
legend("topright", byloans_gender$`Loan Purpose`, cex = 0.7, fill = bar_colors)
dev.off()

## The most basic plot() function is used throughout this R script. You are free to use other plotting packages 
## AS LONG AS deliver the required result in assignment. Be sure to use robust and bug-free
## packages. ggplot and ggplot2 are among recommended ones.


```


### Useful Functions for Computations

```{r}

mean(credit$Savings)

median(credit$Savings)

var(credit$Savings) # variance

sd(credit$Savings)

max(credit$Savings)

min(credit$Savings)

range(credit$Savings)

quantile(credit$Savings)

quantile(credit$Savings,c(.3,.6,.9))

table(credit$Gender)

cor(credit$Savings, credit$Age) # correlation

rowMeans(credit[, c("Savings", "Checking")]) # compute mean at each row
rowSums(credit[, c("Savings", "Checking")]) # compute sum at each row
```


