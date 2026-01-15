#Load the necessary libraries
install.packages("skimr")
install.packages("dplyr")
install.packages("janitor")
install.packages("here")
install.packages("tidyverse")
install.packages("tidyr")
library(tidyverse)
library(skimr)
library(dplyr)
library(janitor)
library(here)
library(tidyr)
#Load the dataset
data(quakes)
# Check the structure of the dataset
View(quakes)
# Check the first few rows of the dataset
head(quakes)
# Check the column names
colnames(quakes)
#use the skimr package to get a summary of the dataset
skim_without_charts(quakes)
#rename the columns ,drop missing values, filter the data with mag > 4.5 and arrange the data by number of stations
quakes_df <- quakes %>%
  rename("Number_of_Stations" = "stations")  %>%
    drop_na(mag) %>%
    remove_empty("rows") %>%
    filter(mag > 4.5) %>%
    arrange(desc(Number_of_Stations))

# Check the structure of the cleaned dataset
str(quakes_df)
# Check the first few rows of the cleaned dataset
head(quakes_df)
# Check the column names of the cleaned dataset
colnames(quakes_df)
# Check the summary of the cleaned dataset
summary(quakes_df)
# Check the number of rows and columns in the cleaned dataset
dim(quakes_df)
# Check the number of rows and columns in the original dataset
dim(quakes)
# Check the number of rows and columns in the cleaned dataset
nrow(quakes_df)
ncol(quakes_df)
# Check the number of rows and columns in the original dataset
nrow(quakes)
ncol(quakes)
View(quakes_df)
#check the correlation between the magnitude and number of stations
cor(quakes_df$mag, quakes_df$Number_of_Stations)
#add a new column to the cleaned dataset
quakes_df <- quakes_df %>%
    mutate(mag_level = case_when(
        mag >= 4.5 & mag < 5.5 ~ "Medium",
        mag >= 5.5 ~ "High"
    )) %>%
    mutate(Intensity_Index= mag * Number_of_Stations)
# Check the structure of the cleaned datasetView(quakes_df)

library(ggplot2)
#code to create a scatter plot
ggplot(data = quakes_df, aes(x = mag, y = Number_of_Stations)) +
  geom_smooth(aes(color = mag_level), size = 3) +
  labs(title = "Magnitude vs Number of Stations",
       x = "Magnitude",
       y = "Number of Stations") +
  theme_minimal()
#code to create a histogram
ggplot(data = quakes_df, aes(x = mag)) +
  geom_histogram(binwidth = 0.5, fill = "blue", color = "black") +
  labs(title = "Histogram of Magnitude",
       x = "Magnitude",
       y = "Frequency") +
  theme_minimal()

write_csv(quakes_df, "/Users/utkarshtyagi/Documents/VSC/Dataset/quakes_df.csv")


