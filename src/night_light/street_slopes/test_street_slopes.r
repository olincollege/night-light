if (!require(testthat)) install.packages("testthat")
if (!require(testthat)) install.packages("sf")
library(sf)
library(testthat)

# Test data
test_data <- st_sf(
  id = 1:3,
  geometry = st_sfc(
    st_point(c(1, 1)),
    st_point(c(2, 2)),
    st_point(c(3, 3))
  )
)

# Test directory and file name
test_dir <- tempdir()
test_file_name <- "test_file.gpkg"

# Test that a file can be created successfully using st_write
test_that("File is created successfully", {
  full_file_path <- file.path(test_dir, test_file_name)

  result <- try({
    st_write(test_data, full_file_path, delete_layer = TRUE)
    TRUE
  }, silent = FALSE)

  expect_true(isTRUE(result), info = "st_write did not complete successfully")
  expect_true(file.exists(full_file_path), info = "File does not exist")
})

# Test that the file is saved at the specified file path
test_that("Returned file path is correct", {
  file_path <- file.path(test_dir, test_file_name)

  result <- tryCatch({
    st_write(test_data, file_path, delete_layer = TRUE)
    file_path
  }, error = function(e) {
    NULL
  })

  expect_equal(result, file_path, info = "Returned file path is not correct")
  expect_true(file.exists(file_path), info = "File does not exist")
})

# Test that the data written using st_write is equal to the input data
test_that("Written data matches input", {
  file_path <- file.path(test_dir, test_file_name)

  saved_path <- tryCatch({
    st_write(test_data, file_path, delete_layer = TRUE)
    file_path
  }, error = function(e) {
    NULL
  })

  written_data <- st_read(saved_path, quiet = TRUE)

  st_crs(written_data) <- st_crs(test_data)

  geometry_col_test <- attr(test_data, "sf_column")
  geometry_col_written <- attr(written_data, "sf_column")

  if (geometry_col_test != geometry_col_written) {
    written_data <- st_set_geometry(written_data, geometry_col_test)

    names(written_data)[names(written_data) == geometry_col_written] <- 
      geometry_col_test
  }
  expect_equal(written_data, test_data, info = "Data does not match input")
})

# Test that a file deletes successfully using file.remove
test_that("File deletes successfully", {
  expect_true(file.exists(full_file_path))
  file.remove(full_file_path)
  expect_false(file.exists(full_file_path))
})