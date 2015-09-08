
This notebook is an attempt to teach new Google Earth Engine users the advantages of using the GEE map methods, and several examples of how to convert a traditional for-loop section of code to a version that uses mapping. 

Author: Christoph Steefel


```python
# Import earth engine and initialize it.
import ee
ee.Initialize()
```


```python
# import the feature collections and other items that will be used.
watershed = ee.FeatureCollection('ft:1A8XfFw11WmvIcOhbU1KkvniNIO_DYfHTJ-FTfdWX')
eastriver = watershed.filter(ee.Filter.Or(ee.Filter.stringContains('name', 'Upper East'),
                            ee.Filter.stringContains('name', 'Middle East')))
startDate = ee.Date('2000-01-01')
precipData = ee.ImageCollection('NASA/ORNL/DAYMET').select(['prcp'])
landsat = ee.ImageCollection('LANDSAT/LT5_L1T')
```

This marks the beginning of the examples. They are in order, but contain  attempts to cache bust between them in order to keep the cache from interfering with the results.

In the following case, the performance of the two is similar, as the computation is nearly the same and not that intensive. (~2s)


```python
%%timeit -n 1 -r 1
# This is an exmaple of iterating through the collection with a for loop
composites = []
ystart = '-01-01'
yend = '-12-31'
col = ee.ImageCollection('LANDSAT/LT5_L1T_32DAY_NDVI')
years = range(1984, 2012)
for year in years:
    # Filter and clip the collection
    median = (col.filterDate(str(year) + ystart, str(year)+yend).median()).clip(eastriver.geometry())
    # Calculate the mean for the watershed
    meanVal = median.reduceRegion(ee.Reducer.mean(), scale=30)
    composites.append(meanVal)
print(ee.List(composites).getInfo())
```

    [{u'NDVI': 0.10028108625084792}, {u'NDVI': 0.06603136052511481}, {u'NDVI': 0.07368777141664831}, {u'NDVI': 0.1471169554260584}, {u'NDVI': 0.15068082005436986}, {u'NDVI': 0.2908393388420323}, {u'NDVI': 0.11869990847476414}, {u'NDVI': 0.15264142999504668}, {u'NDVI': 0.06676839452802721}, {u'NDVI': 0.04505618743963454}, {u'NDVI': 0.08102604098191415}, {u'NDVI': 0.05977321901328999}, {u'NDVI': 0.0766571620786479}, {u'NDVI': 0.06119461399634958}, {u'NDVI': 0.06199115384103681}, {u'NDVI': 0.089313852004698}, {u'NDVI': 0.08554726335659034}, {u'NDVI': 0.06715543477792763}, {u'NDVI': 0.07225472507234791}, {u'NDVI': 0.06227145977717991}, {u'NDVI': 0.08133701861109023}, {u'NDVI': 0.06637010398775961}, {u'NDVI': 0.09298041106307263}, {u'NDVI': 0.08398763301468959}, {u'NDVI': 0.098236305191784}, {u'NDVI': 0.07032105491834283}, {u'NDVI': 0.0798601167883726}, {u'NDVI': 0.07204498788621815}]
    1 loops, best of 1: 1.83 s per loop



```python
x= precipData.limit(5000).getInfo()
```


```python
%%timeit -n 1 -r 1
# Using mapping on the collection
col = ee.ImageCollection('LANDSAT/LT5_L1T_32DAY_NDVI')
def mapFunc(i):
    # Create a yearly median
    median = col.filterDate(date.advance(ee.Number(i), 'year'), date.advance(ee.Number(i).add(ee.Number(1)), 'year'))\
        .median().clip(eastriver.geometry())
        # Return the mean value for the watershed
    return median.reduceRegion(ee.Reducer.mean(), scale=30)
date = ee.Date('1984-01-01')
years = ee.List.sequence(0, 27)
# Map through the numbers corresponding to the numbers of years after 1984 (up to 2011)
composites = years.map(mapFunc)
print(composites.getInfo())
```

    [{u'NDVI': 0.10028108625084792}, {u'NDVI': 0.06603136052511481}, {u'NDVI': 0.07368777141664831}, {u'NDVI': 0.1471169554260584}, {u'NDVI': 0.15068082005436986}, {u'NDVI': 0.2908393388420323}, {u'NDVI': 0.11869990847476414}, {u'NDVI': 0.15264142999504668}, {u'NDVI': 0.06676839452802721}, {u'NDVI': 0.04505618743963454}, {u'NDVI': 0.08102604098191415}, {u'NDVI': 0.05977321901328999}, {u'NDVI': 0.0766571620786479}, {u'NDVI': 0.06119461399634958}, {u'NDVI': 0.06199115384103681}, {u'NDVI': 0.089313852004698}, {u'NDVI': 0.08554726335659034}, {u'NDVI': 0.06715543477792763}, {u'NDVI': 0.07225472507234791}, {u'NDVI': 0.06227145977717991}, {u'NDVI': 0.08133701861109023}, {u'NDVI': 0.06637010398775961}, {u'NDVI': 0.09298041106307263}, {u'NDVI': 0.08398763301468959}, {u'NDVI': 0.098236305191784}, {u'NDVI': 0.07032105491834283}, {u'NDVI': 0.0798601167883726}, {u'NDVI': 0.07204498788621815}]
    1 loops, best of 1: 2.18 s per loop


The next computations have slightly more of a difference, and the mapping version is usually faster. The difference between the pieces of code is still small however.


```python
%%timeit -n 1 -r 1
# Using a for loop for aggregation by date.
result = []
for i in range(0, 366, 5):
    # filter to the 5 day region defined by i and i+5, sum, and clip the image
    sum = precipData.filterDate(startDate.advance(i, 'day'), startDate.advance(i+5, 'day')).sum()\
        .clip(eastriver.geometry())
    # Calculate the mean precipitation 
    result.append(sum.reduceRegion(ee.Reducer.mean(), scale=30))
print(ee.List(result).getInfo())
```

    [{u'prcp': 27.314198124308593}, {u'prcp': 12.315825188467135}, {u'prcp': 2.9342125594213897}, {u'prcp': 22.98399187144802}, {u'prcp': 47.907048157574984}, {u'prcp': 21.758396612278396}, {u'prcp': 7.28621246057603}, {u'prcp': 3.714570933268781}, {u'prcp': 67.17812836076422}, {u'prcp': 25.777006281248866}, {u'prcp': 7.106404649194199}, {u'prcp': 39.74517053314551}, {u'prcp': 8.04285731049844}, {u'prcp': 33.68238323867229}, {u'prcp': 19.931780353828234}, {u'prcp': 17.34795865426729}, {u'prcp': 10.696869696772154}, {u'prcp': 10.896639032141815}, {u'prcp': 18.07048173594963}, {u'prcp': 0.0}, {u'prcp': 4.013759195465761}, {u'prcp': 13.671505719015444}, {u'prcp': 24.31387861897142}, {u'prcp': 2.3419251399094927}, {u'prcp': 0.0}, {u'prcp': 23.68129413699416}, {u'prcp': 2.6659643490117437}, {u'prcp': 9.095374776256195}, {u'prcp': 3.5045245400124436}, {u'prcp': 10.226512923355168}, {u'prcp': 0.0}, {u'prcp': 0.0}, {u'prcp': 4.607903010074713}, {u'prcp': 0.0}, {u'prcp': 20.008690324893937}, {u'prcp': 13.082436682472972}, {u'prcp': 1.2992955983679209}, {u'prcp': 0.0}, {u'prcp': 17.036794078439822}, {u'prcp': 35.419596777255784}, {u'prcp': 0.0}, {u'prcp': 2.3161645790315517}, {u'prcp': 0.0}, {u'prcp': 0.0}, {u'prcp': 16.650602880838857}, {u'prcp': 18.293955583812018}, {u'prcp': 26.76205465301517}, {u'prcp': 15.018353083455942}, {u'prcp': 4.984423499027825}, {u'prcp': 9.513274780918128}, {u'prcp': 23.180021342275893}, {u'prcp': 0.0}, {u'prcp': 11.574895815827885}, {u'prcp': 15.48383667455895}, {u'prcp': 6.212545944286781}, {u'prcp': 11.341015285632052}, {u'prcp': 0.0}, {u'prcp': 2.380887348926343}, {u'prcp': 0.0}, {u'prcp': 12.664586821425232}, {u'prcp': 13.609253903872673}, {u'prcp': 24.939238355347317}, {u'prcp': 13.474726396896246}, {u'prcp': 18.93417371013577}, {u'prcp': 3.1065810930378785}, {u'prcp': 0.0}, {u'prcp': 0.537991617685865}, {u'prcp': 0.0}, {u'prcp': 30.170676807425274}, {u'prcp': 44.217208939949906}, {u'prcp': 15.758166059790241}, {u'prcp': 8.71027286056189}, {u'prcp': 0.0}, {u'prcp': 0.020708031036494292}]
    1 loops, best of 1: 2.35 s per loop



```python
x = landsat.limit(5000).getInfo()
```


```python
%%timeit -n 1 -r 1
# with mapping
def aggregator(i):
    i = ee.Number(i)
    start = startDate.advance(i.multiply(5), 'day')
    end = start.advance(5, 'day')
    # Filter to the 5 day period, sum, and clip
    sum = precipData.filterDate(start, end).sum().clip(eastriver.geometry())
    # return the mean value.
    return sum.reduceRegion(ee.Reducer.mean(), scale=30)
# The steps to map with are numbers becuase this allows us to properly aggregate over each 5-day period.
steps = ee.List.sequence(0, 365/5)
res = steps.map(aggregator)
print(res.getInfo())
```

    [{u'prcp': 27.314198124308593}, {u'prcp': 12.315825188467135}, {u'prcp': 2.9342125594213897}, {u'prcp': 22.98399187144802}, {u'prcp': 47.907048157574984}, {u'prcp': 21.758396612278396}, {u'prcp': 7.28621246057603}, {u'prcp': 3.714570933268781}, {u'prcp': 67.17812836076422}, {u'prcp': 25.777006281248866}, {u'prcp': 7.106404649194199}, {u'prcp': 39.74517053314551}, {u'prcp': 8.04285731049844}, {u'prcp': 33.68238323867229}, {u'prcp': 19.931780353828234}, {u'prcp': 17.34795865426729}, {u'prcp': 10.696869696772154}, {u'prcp': 10.896639032141815}, {u'prcp': 18.07048173594963}, {u'prcp': 0.0}, {u'prcp': 4.013759195465761}, {u'prcp': 13.671505719015444}, {u'prcp': 24.31387861897142}, {u'prcp': 2.3419251399094927}, {u'prcp': 0.0}, {u'prcp': 23.68129413699416}, {u'prcp': 2.6659643490117437}, {u'prcp': 9.095374776256195}, {u'prcp': 3.5045245400124436}, {u'prcp': 10.226512923355168}, {u'prcp': 0.0}, {u'prcp': 0.0}, {u'prcp': 4.607903010074713}, {u'prcp': 0.0}, {u'prcp': 20.008690324893937}, {u'prcp': 13.082436682472972}, {u'prcp': 1.2992955983679209}, {u'prcp': 0.0}, {u'prcp': 17.036794078439822}, {u'prcp': 35.419596777255784}, {u'prcp': 0.0}, {u'prcp': 2.3161645790315517}, {u'prcp': 0.0}, {u'prcp': 0.0}, {u'prcp': 16.650602880838857}, {u'prcp': 18.293955583812018}, {u'prcp': 26.76205465301517}, {u'prcp': 15.018353083455942}, {u'prcp': 4.984423499027825}, {u'prcp': 9.513274780918128}, {u'prcp': 23.180021342275893}, {u'prcp': 0.0}, {u'prcp': 11.574895815827885}, {u'prcp': 15.48383667455895}, {u'prcp': 6.212545944286781}, {u'prcp': 11.341015285632052}, {u'prcp': 0.0}, {u'prcp': 2.380887348926343}, {u'prcp': 0.0}, {u'prcp': 12.664586821425232}, {u'prcp': 13.609253903872673}, {u'prcp': 24.939238355347317}, {u'prcp': 13.474726396896246}, {u'prcp': 18.93417371013577}, {u'prcp': 3.1065810930378785}, {u'prcp': 0.0}, {u'prcp': 0.537991617685865}, {u'prcp': 0.0}, {u'prcp': 30.170676807425274}, {u'prcp': 44.217208939949906}, {u'prcp': 15.758166059790241}, {u'prcp': 8.71027286056189}, {u'prcp': 0.0}, {u'prcp': 0.020708031036494292}]
    1 loops, best of 1: 1.63 s per loop



```python
landsat = ee.ImageCollection('LANDSAT/LT5_L1T')
landsat = landsat.filterDate('2000-01-01', '2000-12-31').filterBounds(eastriver.geometry())
# 365 is arbitrary, but larger than the number of possible images in the collection.
lst = landsat.toList(365)
```

The following example shows mapping as much faster. Landsat is converted to a list in order to allow the mapping to return a non-Feature and non-Image item. Generally when mapping, an Image is returned, and so conversion to a list is unneeded. Both these examples would fail if the collection had over 5000 elements, but the mapping version could be changed to use the ImageCollection and return Features that could be exported, getting around the limit to some extent.


```python
%%timeit -n 1 -r 1 # Calculate the NDVI by hand and then find the mean NDVI from each scene. for-loop
length = lst.length().getInfo()
means = []
for i in range(length):
    img = ee.Image(lst.get(i))
    # calculate the NDVI
    img = img.normalizedDifference(['B4', 'B3']).clip(eastriver.geometry())
    # Calculate the mean NDVI for the region
    means.append(img.reduceRegion(ee.Reducer.mean(), scale=30))
print(ee.List(means).getInfo())
```

    [{u'nd': -0.09080041725518817}, {u'nd': -0.0577632996436818}, {u'nd': -0.0898644790287846}, {u'nd': -0.09685885722396875}, {u'nd': -0.05084229286192648}, {u'nd': 0.0964246615705362}, {u'nd': -0.0032693602243703784}, {u'nd': 0.16657020902014982}, {u'nd': 0.24293099765399528}, {u'nd': 0.35166942258574757}, {u'nd': -0.0306726125865453}, {u'nd': 0.2846917356841681}, {u'nd': 0.29315717326071256}, {u'nd': 0.11700711031661762}, {u'nd': 0.18281540248980663}, {u'nd': -0.02358583953868348}, {u'nd': -0.07358403006146398}, {u'nd': -0.040772686997260596}, {u'nd': -0.07107349344101457}, {u'nd': -0.052735115088967395}, {u'nd': -0.07823373019069566}, {u'nd': -0.11342093544219707}, {u'nd': -0.06768029013604737}, {u'nd': -0.05915361897413456}, {u'nd': 0.202927172115082}, {u'nd': 0.3630570008765785}, {u'nd': 0.05536616064676066}, {u'nd': 0.3962040517724982}, {u'nd': 0.21729903576164886}, {u'nd': 0.30479740948024336}, {u'nd': 0.3374369829843147}, {u'nd': 0.09180466177949793}, {u'nd': 0.04253701011623666}, {u'nd': -0.052415940593029293}, {u'nd': -0.07830174383199823}]
    1 loops, best of 1: 3.85 s per loop



```python
# Cache bust
x = precipData.limit(5000).getInfo()
```


```python
%%timeit -n 1 -r 1 # Calculate the NDVI in a mapped function, then create a feature with the data.
def getMeans(img):
    # Calculate the NDVI
    img = ee.Image(img).normalizedDifference(['B4', 'B3']).clip(eastriver.geometry())
    # Calculate  the regional mean
    return img.reduceRegion(ee.Reducer.mean(), scale=30)
# Uses a list so that we don't have to return an Image or Feature.
results = lst.map(getMeans)
print(results.getInfo())
```

    [{u'nd': -0.09080041725518817}, {u'nd': -0.0577632996436818}, {u'nd': -0.0898644790287846}, {u'nd': -0.09685885722396875}, {u'nd': -0.05084229286192648}, {u'nd': 0.0964246615705362}, {u'nd': -0.0032693602243703784}, {u'nd': 0.16657020902014982}, {u'nd': 0.24293099765399528}, {u'nd': 0.35166942258574757}, {u'nd': -0.0306726125865453}, {u'nd': 0.2846917356841681}, {u'nd': 0.29315717326071256}, {u'nd': 0.11700711031661762}, {u'nd': 0.18281540248980663}, {u'nd': -0.02358583953868348}, {u'nd': -0.07358403006146398}, {u'nd': -0.040772686997260596}, {u'nd': -0.07107349344101457}, {u'nd': -0.052735115088967395}, {u'nd': -0.07823373019069566}, {u'nd': -0.11342093544219707}, {u'nd': -0.06768029013604737}, {u'nd': -0.05915361897413456}, {u'nd': 0.202927172115082}, {u'nd': 0.3630570008765785}, {u'nd': 0.05536616064676066}, {u'nd': 0.3962040517724982}, {u'nd': 0.21729903576164886}, {u'nd': 0.30479740948024336}, {u'nd': 0.3374369829843147}, {u'nd': 0.09180466177949793}, {u'nd': 0.04253701011623666}, {u'nd': -0.052415940593029293}, {u'nd': -0.07830174383199823}]
    1 loops, best of 1: 2.59 s per loop



```python
# This saves various variables and defines functions for use in the following cells.
import time
meadow = ee.FeatureCollection('ft:1UhHMn17CQWhgeELhXGOMPwLCYLdKjBtkcHarn6AN')
landsatData = ee.ImageCollection('LEDAPS/LT5_L1T_SR').select(['B3', 'B4', 'QA']).filterDate('1995-01-01', '2005-12-31')
landsatData = landsatData.filter(ee.Filter.Or(ee.Filter.equals('WRS_PATH', 35), ee.Filter.equals('WRS_PATH', 34)))\
                        .filterMetadata('WRS_ROW', 'equals', 33)
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
```

The following example involves exporting, so the timing is also dependent on how long the export takes, which can vary quite a bit. However, the times should still reflect the improved performance of using mapping. 



```python
%%timeit -n 1 -r 1 # For loop version
lst = landsatData.toList(5000)
points = meadow.toList(100)
plength = points.length().getInfo()
length = lst.length().getInfo()
results = []

for i in range(length):
    img = ee.Image(lst.get(i))
    img = calcNDVI(img)
    for j in range(plength):
        point = ee.Feature(points.get(j)).geometry()
        results.append(img.sample(point, 30))
results = ee.FeatureCollection(results).flatten()
task = ee.batch.Export.table(results, 'forTest', {'fileFormat': 'CSV'})
task.start()
# This would never be included in a normal script, but blocks the script until the export
# is done in order to represent the total time of all calculations.
while task.active():
    # Requires a sleep to not spam google servers. Has a negligible effect on timing.
    time.sleep(5)
print(task.status()['state'])
```

    COMPLETED
    1 loops, best of 1: 5min 27s per loop



```python
# Cache busting
x = precipData.limit(5000).getInfo()
```


```python
%%timeit -n 1 -r 1  #Map version
results = ee.FeatureCollection(landsatData.map(mappedSample)).flatten()
task = ee.batch.Export.table(results, 'mapTest', {'fileFormat': 'CSV'})
task.start()
# This would never be included in a normal script, but blocks the script until the export
# is done in order to represent the total time of all calculations.
while task.active():
    # requires a sleep to not spam google servers.
    time.sleep(5)
print(task.status()['state'])
```

    COMPLETED
    1 loops, best of 1: 4min 51s per loop


Obviously, the map version is simpler, and provides the advantage of using potentially reusable functions. For example, maskClouds is usable for cloud masking with any LEDAPS surface reflectance image. The outputs are slightly different, as the mapped version keeps the Landsat scene id in the system_index.


```python
# Identifying days in which the Daymet max temp surpasses 15 degrees in the entire eastriver watershed for some of 2011.
tempData = ee.ImageCollection('NASA/ORNL/DAYMET').select('tmax')
tempData = tempData.filterDate('2011-01-01', '2011-12-31')
tempData = tempData.toList(365)
```


```python
%%timeit -n 1 -r 1 # Use a for-loop
length = tempData.length().getInfo()
results = []
for i in range(length):
    img = ee.Image(tempData.get(i))
    result = ee.Number(ee.Image(img.gt(15)).reduceRegion(ee.Reducer.mean(), eastriver.geometry(),
                                                     scale=1000).get('tmax'))
    results.append(ee.Algorithms.If(result.eq(1), 1, 0))
print(ee.List(results).getInfo())
```

    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    1 loops, best of 1: 4.23 s per loop



```python
# Cache busting
x = precipData.limit(5000).getInfo()
```


```python
%%timeit -n 1 -r 1 # Use a map mathod
def findHighTemp(img):
    result = ee.Image(img).gt(15).reduceRegion(ee.Reducer.mean(), eastriver.geometry(), scale=1000).get('tmax')
    return ee.Algorithms.If(ee.Number(result).eq(1), 1, 0)
print(tempData.map(findHighTemp).getInfo())
```

    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    1 loops, best of 1: 2.29 s per loop


The for-loop is significantly slower, as it takes less advantage of parallelization.


```python

```
