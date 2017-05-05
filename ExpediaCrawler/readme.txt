1. Set up a new scrapy projec: scarpy startproject xxx
2. replace xxx's code with those in ExpediaCrawler
3. open www.expedia.com.au, type in target destination, valid check in and check out data and click search.
4. right click on chrome to trigger the drop down menue, find inspection at the bottom. 
5. find Network tab in the inspection window,refresh the entire page.
6. find a package named "Hotel-Search-Data?responsive=true" and look at its header,form which find regionId and destination and use them to replace the corresponding ones in the source code.