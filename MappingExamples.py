
# coding: utf-8

# This notebook is an attempt to teach new Google Earth Engine users the advantages of using the GEE map methods, and several examples of how to convert a traditional for-loop section of code to a version that uses mapping. 
# 
# Author: Christoph Steefel

# In[1]:

# Import earth engine and initialize it.
import ee
ee.Initialize()


# In[2]:

# import the feature collections and other items that will be used.
watershed = ee.FeatureCollection('ft:1A8XfFw11WmvIcOhbU1KkvniNIO_DYfHTJ-FTfdWX')
eastriver = watershed.filter(ee.Filter.Or(ee.Filter.stringContains('name', 'Upper East'),
                            ee.Filter.stringContains('name', 'Middle East')))
startDate = ee.Date('2000-01-01')
precipData = ee.ImageCollection('NASA/ORNL/DAYMET').select(['prcp'])
landsat = ee.ImageCollection('LANDSAT/LT5_L1T')


# This marks the beginning of the examples. They are in order, but contain  attempts to cache bust between them in order to keep the cache from interfering with the results.

# In the following case, the performance of the two is similar, as the computation is nearly the same and not that intensive. (~2s)

# In[3]:

get_ipython().run_cell_magic(u'timeit', u'-n 1 -r 1', u"# This is an exmaple of iterating through the collection with a for loop\ncomposites = []\nystart = '-01-01'\nyend = '-12-31'\ncol = ee.ImageCollection('LANDSAT/LT5_L1T_32DAY_NDVI')\nyears = range(1984, 2012)\nfor year in years:\n    # Filter and clip the collection\n    median = (col.filterDate(str(year) + ystart, str(year)+yend).median()).clip(eastriver.geometry())\n    # Calculate the mean for the watershed\n    meanVal = median.reduceRegion(ee.Reducer.mean(), scale=30)\n    composites.append(meanVal)\nprint(ee.List(composites).getInfo())")


# In[4]:

x= precipData.limit(5000).getInfo()


# In[5]:

get_ipython().run_cell_magic(u'timeit', u'-n 1 -r 1', u"# Using mapping on the collection\ncol = ee.ImageCollection('LANDSAT/LT5_L1T_32DAY_NDVI')\ndef mapFunc(i):\n    # Create a yearly median\n    median = col.filterDate(date.advance(ee.Number(i), 'year'), date.advance(ee.Number(i).add(ee.Number(1)), 'year'))\\\n        .median().clip(eastriver.geometry())\n        # Return the mean value for the watershed\n    return median.reduceRegion(ee.Reducer.mean(), scale=30)\ndate = ee.Date('1984-01-01')\nyears = ee.List.sequence(0, 27)\n# Map through the numbers corresponding to the numbers of years after 1984 (up to 2011)\ncomposites = years.map(mapFunc)\nprint(composites.getInfo())")


# The next computations have slightly more of a difference, and the mapping version is usually faster. The difference between the pieces of code is still small however.

# In[6]:

get_ipython().run_cell_magic(u'timeit', u'-n 1 -r 1', u"# Using a for loop for aggregation by date.\nresult = []\nfor i in range(0, 366, 5):\n    # filter to the 5 day region defined by i and i+5, sum, and clip the image\n    sum = precipData.filterDate(startDate.advance(i, 'day'), startDate.advance(i+5, 'day')).sum()\\\n        .clip(eastriver.geometry())\n    # Calculate the mean precipitation \n    result.append(sum.reduceRegion(ee.Reducer.mean(), scale=30))\nprint(ee.List(result).getInfo())")


# In[7]:

x = landsat.limit(5000).getInfo()


# In[8]:

get_ipython().run_cell_magic(u'timeit', u'-n 1 -r 1', u"# with mapping\ndef aggregator(i):\n    i = ee.Number(i)\n    start = startDate.advance(i.multiply(5), 'day')\n    end = start.advance(5, 'day')\n    # Filter to the 5 day period, sum, and clip\n    sum = precipData.filterDate(start, end).sum().clip(eastriver.geometry())\n    # return the mean value.\n    return sum.reduceRegion(ee.Reducer.mean(), scale=30)\n# The steps to map with are numbers becuase this allows us to properly aggregate over each 5-day period.\nsteps = ee.List.sequence(0, 365/5)\nres = steps.map(aggregator)\nprint(res.getInfo())")


# In[9]:

landsat = ee.ImageCollection('LANDSAT/LT5_L1T')
landsat = landsat.filterDate('2000-01-01', '2000-12-31').filterBounds(eastriver.geometry())
# 365 is arbitrary, but larger than the number of possible images in the collection.
lst = landsat.toList(365)


# The following example shows mapping as much faster. Landsat is converted to a list in order to allow the mapping to return a non-Feature and non-Image item. Generally when mapping, an Image is returned, and so conversion to a list is unneeded. Both these examples would fail if the collection had over 5000 elements, but the mapping version could be changed to use the ImageCollection and return Features that could be exported, getting around the limit to some extent.

# In[10]:

get_ipython().run_cell_magic(u'timeit', u'-n 1 -r 1 # Calculate the NDVI by hand and then find the mean NDVI from each scene. for-loop', u"length = lst.length().getInfo()\nmeans = []\nfor i in range(length):\n    img = ee.Image(lst.get(i))\n    # calculate the NDVI\n    img = img.normalizedDifference(['B4', 'B3']).clip(eastriver.geometry())\n    # Calculate the mean NDVI for the region\n    means.append(img.reduceRegion(ee.Reducer.mean(), scale=30))\nprint(ee.List(means).getInfo())")


# In[11]:

# Cache bust
x = precipData.limit(5000).getInfo()


# In[12]:

get_ipython().run_cell_magic(u'timeit', u'-n 1 -r 1 # Calculate the NDVI in a mapped function, then create a feature with the data.', u"def getMeans(img):\n    # Calculate the NDVI\n    img = ee.Image(img).normalizedDifference(['B4', 'B3']).clip(eastriver.geometry())\n    # Calculate  the regional mean\n    return img.reduceRegion(ee.Reducer.mean(), scale=30)\n# Uses a list so that we don't have to return an Image or Feature.\nresults = lst.map(getMeans)\nprint(results.getInfo())")


# In[3]:

# This saves various variables and defines functions for use in the following cells.
import time
meadow = ee.FeatureCollection('ft:1UhHMn17CQWhgeELhXGOMPwLCYLdKjBtkcHarn6AN')
landsatData = ee.ImageCollection('LEDAPS/LT5_L1T_SR').select(['B3', 'B4', 'QA']).filterDate('1995-01-01', '2005-12-31')
landsatData = landsatData.filter(ee.Filter.Or(ee.Filter.equals('WRS_PATH', 35), ee.Filter.equals('WRS_PATH', 34)))                        .filterMetadata('WRS_ROW', 'equals', 33)
points = meadow
def calcNDVI(img):
    """ Calculates NDVI, keeps date values"""
    img = maskClouds(img).clip(watershed)
    img = img.normalizedDifference(['B4', 'B3']).rename(['NDVI']).addBands(img.metadata('system:time_start'))
    return img

def maskClouds(image):                                                          
    """ Masks clouds based on bits pulled from the LEDAPS QA band."""              
    sc = image.select('QA')                                                        
    return image.mask(image.mask().And(                                            
                      sc.bitwiseNot().bitwiseAnd(ee.Image(0x6000)))) 

def mappedSample(img):
    """ Combines all steps of masking clouds, calculating NDVI, and sampling the points into one."""
    img = maskClouds(img).clip(watershed)
    img = img.normalizedDifference(['B4', 'B3']).rename(['NDVI']).addBands(img.metadata('system:time_start'))
    result = points.map(lambda ft: img.sample(ee.Feature(ft).geometry(), scale=30))
    return result.flatten()


# The following example involves exporting, so the timing is also dependent on how long the export takes, which can vary quite a bit. However, the times should still reflect the improved performance of using mapping. 
# 

# In[4]:

get_ipython().run_cell_magic(u'timeit', u'-n 1 -r 1 # For loop version', u"lst = landsatData.toList(5000)\npoints = meadow.toList(100)\nplength = points.length().getInfo()\nlength = lst.length().getInfo()\nresults = []\n\nfor i in range(length):\n    img = ee.Image(lst.get(i))\n    img = calcNDVI(img)\n    for j in range(plength):\n        point = ee.Feature(points.get(j)).geometry()\n        results.append(img.sample(point, 30))\nresults = ee.FeatureCollection(results).flatten()\ntask = ee.batch.Export.table(results, 'forTest', {'fileFormat': 'CSV'})\ntask.start()\n# This would never be included in a normal script, but blocks the script until the export\n# is done in order to represent the total time of all calculations.\nwhile task.active():\n    # Requires a sleep to not spam google servers. Has a negligible effect on timing.\n    time.sleep(5)\nprint(task.status()['state'])")


# In[5]:

# Cache busting
x = precipData.limit(5000).getInfo()


# In[6]:

get_ipython().run_cell_magic(u'timeit', u'-n 1 -r 1  #Map version', u"results = ee.FeatureCollection(landsatData.map(mappedSample)).flatten()\ntask = ee.batch.Export.table(results, 'mapTest', {'fileFormat': 'CSV'})\ntask.start()\n# This would never be included in a normal script, but blocks the script until the export\n# is done in order to represent the total time of all calculations.\nwhile task.active():\n    # requires a sleep to not spam google servers.\n    time.sleep(5)\nprint(task.status()['state'])")


# Obviously, the map version is simpler, and provides the advantage of using potentially reusable functions. For example, maskClouds is usable for cloud masking with any LEDAPS surface reflectance image. The outputs are slightly different, as the mapped version keeps the Landsat scene id in the system_index.

# In[ ]:



