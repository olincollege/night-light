# Load required libraries
library(dplyr)
library(geodist)
library(osmextract)
library(raster)
library(remotes)
library(sf)
library(slopes)
library(stplanr)

install_libraries <- function() {
  if (!require(dplyr)) install.packages("dplynr")
  if (!require(geodist)) install.packages("geodist")
  if (!require(raster)) install.packages("raster")
  if (!require(remotes)) install.packages("remotes")
  if (!require(sf)) install.packages("sf")
  if (!require(slopes)) install.packages("slopes")
  if (!require(stplanr)) install.packages("stplanr")

  if (!require("osmextract"))
    remotes::install_github("ITSLeeds/osmextract")
  if (!require("stplanr"))
    remotes::install_github("ropensci/stplanr")
  if (!require("mapview"))
    remotes::install_github("r-spatial/mapview")
}

install_libraries()

mass_osm <- oe_get("us/massachusetts", provider = "geofabrik",
                   stringsAsFactors = FALSE,
                   quiet = FALSE, force_download = TRUE,
                   force_vectortranslate = TRUE)

# Filter major roads
mass_network <- mass_osm %>%
  filter(.data$highway %in% c("primary", "primary_link", "secondary",
                              "secondary_link", "tertiary", "tertiary_link",
                              "trunk", "trunk_link", "residential",
                              "cycleway", "living_street", "unclassified",
                              "motorway", "motorway_link", "pedestrian",
                              "steps", "track"))

# Remove unconnected roads
mass_network$group <- rnet_group(mass_network)
mass_network_clean <- mass_network %>% filter(.data$group == 1)
mass_network_segments <- rnet_breakup_vertices(mass_network_clean)

# Import and plot DEM
u <- "https://dds.cr.usgs.gov/download-staging/eyJpZCI6NzAwNjkyNjczLCJjb250YWN0SWQiOjI3MzQwMTg0fQ=="
f <- basename(u)
download.file(url = u, destfile = f, mode = "wb")
dem <- raster::raster(f)
network <- mass_network_segments

network$slope <- slope_raster(network, dem)
network$slope <- network$slope * 100
summary(network$slope)

# Classify slopes
network$slope_class <- network$slope %>%
  cut(
    breaks = c(0, 3, 5, 8, 10, 20, Inf),  # Define the slope breakpoints
    labels = c("0-3: flat", "3-5: mild", "5-8: medium", "8-10: hard",
               "10-20: extreme", ">20: impossible"),
    right = FALSE
  )

# Calculate the percentage of segments in each slope category
slope_percentages <- round(prop.table(table(network$slope_class)) * 100, 1)
st_write(network, "test_street_elevation.geojson")

# Delete DEM file
if (file.exists("eyJpZCI6NzAwNjkyNjczLCJjb250YWN0SWQiOjI3MzQwMTg0fQ==")) {
  file.remove("eyJpZCI6NzAwNjkyNjczLCJjb250YWN0SWQiOjI3MzQwMTg0fQ==")
  message("File deleted successfully.")
} else {
  message("File does not exist.")
}