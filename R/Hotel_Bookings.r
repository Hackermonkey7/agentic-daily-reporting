#Hotel Bookings Analysis
# Load necessary libraries
library(tidyverse)
bookings_df <- read.csv("/Users/utkarshtyagi/Documents/VSC/Dataset/hotel_bookings.csv")
# Check the structure of the dataset
str(bookings_df)
head(bookings_df)
#column names
colnames(bookings_df)
#create new dataframe
new_df <- select(bookings_df, `adr`, adults)
#create new variable in dataframe
mutate(new_df, total = `adr` / adults)
#upload the data
write_csv(
  new_df, "/Users/utkarshtyagi/Documents/VSC/Dataset/hotel_bookings_new.csv"
)
-------------------

# Data Cleaning
skim_without_charts(bookings_df)
trimmed_df <- bookings_df %>%
select("hotel", "is_canceled", "lead_time")
trimmed_df %>%
  select(hotel, is_canceled, lead_time) %>% 
  rename( "Hotel_type" = "hotel")
colnames(trimmed_df)