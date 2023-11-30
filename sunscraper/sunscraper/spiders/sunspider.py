import scrapy
from scrapy.http import FormRequest


class SunspiderSpider(scrapy.Spider):
    name = "sunspider"
    allowed_domains = ["reg.bom.gov.au"]
    start_urls = ["https://reg.bom.gov.au/climate/data/index.shtml?bookmark=193"]

    def parse(self, response):

        # gets station number passed to scrapy spider
        station_number = getattr(self, 'station_number', None)

        print("*************************", station_number)
        # form data needed to get url for solar radiation data, where:
        # p_stn_num is the local station number
        # p_nccObsCode is the observation i.e. solar radiation. This input is hidden in the html
        # p_display_type is the data points i.e. daily. This input is hidden in the html
        formdata = {
            'p_nccObsCode': '193',
            'p_display_type': 'dailyDataFile',
            'p_stn_num': station_number,
        }

        # xpath for the submit button on the form
        submit_button_xpath = response.xpath('//input[@id="getData"]')
        
        # fills in and submits the form, retrieving the url and passing to afdter_submit method
        yield FormRequest.from_response(
            response,
            formid="climatedata",
            formdata=formdata,
            clickdata={'xpath': submit_button_xpath},
            callback=self.after_submit
        )

    
    def after_submit(self, response):
        
        # # get mean data and months from table for all years
        table_data = response.xpath('//*[@id="statsTable"]//tbody//tr')
        table_months = response.xpath('//*[@id="statsTable"]/thead//th')

        # extracts list of mean values for each month
        mean_list = table_data[0].css('td ::text').extract() 
        months_list = table_months.css('th ::text').extract()

        # iterates through data and appends to mean_data list of dictionaries
        for i in range(12):
            month = months_list[i + 1]
            mean = mean_list[i]
            yield{
                "month": month, 
                "mean": float(mean),
            }            