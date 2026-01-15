#Load the necessary libraries
install.packages("skimr")
install.packages("dplyr")
install.packages("janitor")
install.packages("here")
install.packages("tidyverse")
install.packages("tidyr")
install.packages("ggplot2")
install.packages("readr")
install.packages("openair")
library(tidyverse)
library(viridis)
library(skimr)
library(dplyr)
library(janitor)
library(here)
library(tidyr)
library(ggplot2)
library(readr)
library(openair)
#read the dataset
Climate_airport_df <- read_csv("/Users/utkarshtyagi/Documents/VSC/Dataset/Climate_airport_Comp.csv")
# Check the structure of the dataset
View(Climate_airport_df)
# Check the first few rows of the dataset
head(Climate_airport_df)
# Check the column names    
colnames(Climate_airport_df)
#use the skimr package to get a summary of the dataset
skim_without_charts(Climate_airport_df)

#clean the dataset
airport_df <- Climate_airport_df %>%
  rename("Station-Airport" = "station")  %>%
  drop_na("Wind Direction") %>%
 group_by(`Station-Airport`) %>%
  mutate(Temperature = case_when(
    `Air Temp` >= 0 & `Air Temp` < 75 ~ "Low",
    `Air Temp` >= 75 & `Air Temp` < 90 ~ "Medium",
    `Air Temp` >= 90 ~ "High"
  )) %>%
  mutate(Intensity_Index= `Wind Direction` * `Air Temp`)
# Check the structure of the cleaned dataset
View(airport_df)
skim_without_charts(airport_df)
# Rmove column Intensity_Index
airport_df <- airport_df %>%
  select(-`Intensity_Index`)
# Check the structure of the cleaned dataset
View(airport_df)

airport_df <- airport_df %>%
    mutate(Severity = if_else(!is.na(`Wind Speed`) & !is.na(Visibility), 
                              `Wind Speed` * Visibility, 
                              NA_real_))
#check correlation between Wind Speed and Visibility
cor(airport_df$`Wind Speed`,airport_df$Visibility)
#calculate the mean metrics of different groups-
airport_df_mean <- airport_df %>%
    group_by(Station_Airport) %>%
    summarise(mean_severity = mean(Severity, na.rm= TRUE),
      mean_humidity = mean(Humidity, na.rm=TRUE), 
      mean_temp = mean(`Air Temp`, na.rm=TRUE),
      mean_wind_speed= mean(Wind_Speed,na.rm=TRUE),
      mean_visibility = mean(Visibility,na.rm=TRUE)
      )
View(airport_df_mean)

# Ensure Wind Speed and Wind Direction are numeric and have no missing values
airport_df <- airport_df %>%
  filter(!is.na(`Wind Speed`) & !is.na(`Wind Direction`)) %>%
  mutate(`Wind Speed` = as.numeric(`Wind Speed`),
         `Wind Direction` = as.numeric(`Wind Direction`))


#Rename Columns for Wind rose Plot
airport_df <- airport_df %>%
  rename(Wind_Speed = `Wind Speed`, Wind_Direction = `Wind Direction`, Station_Airport = `Station-Airport`)
  colnames(airport_df)

# Plot the data to display wind direction and wind speeds
windRose(airport_df, ws= "Wind_Speed" , wd= "Wind_Direction" , type = "Station_Airport" , cols = "viridis", auto.text = TRUE)

#convert the airport_df_mean to long format
airport_df_mean_long <- airport_df_mean %>%
  pivot_longer(cols = c(mean_severity, mean_humidity, mean_temp, mean_wind_speed, mean_visibility),
               names_to = "Metric",
               values_to = "Mean_Value")
# Check the structure of the long format dataset
View(airport_df_mean_long)
# Plot the data to display Mean Values of different metrics

ggplot(airport_df_mean_long, aes(x = Station_Airport, y = Mean_Value, fill = Station_Airport)) +
  geom_bar(stat = "identity", position = position_dodge(width = 0.8)) +
  geom_text(aes(label = round(Mean_Value, 1)),
            position = position_dodge(width = 0.8),
            vjust = -0.5, size = 3.5) +
  facet_wrap(~Metric, scales = "free_y") +
  labs(title = "Mean Metrics Comparison",
       x = "Station_Airport",
       y = "Mean Value" ,
       fill = "Station_Airport") +
  theme_minimal() 