import puppeteer from 'puppeteer';
import Base from './base.js';

class HouseInfoCrawler extends Base {
    constructor(sessionId) {
        super(sessionId)
        this.name = "houseinfo";
    }

    parse(key, startUrl) {
        console.log("Crawling ", key, " ", startUrl);
        (async () => {
            // Launch the browser and open a new blank page
            const browser = await puppeteer.launch();
            let pn = 1;
            const page = await browser.newPage();
            try {

                await page.goto(startUrl);

                const page1 = await this.getPageResults(page);
                await this.writeOutPath(key, pn, page1.url, page1.html);
                pn = 2;

                //<table cellspacing="0" rules="all" border="1" id="mGrid" style="width:100%;border-collapse:collapse;">
                //    <tbody><tr class="GridHeader">
                //            <th align="left" scope="col">Parcel Number</th><th align="left" scope="col">Location Address</th>
                //            </tr><tr>
                //            <td align="left" style="width:10%;"><a href="ParcelInfo.aspx?parcel_number=27043300200600">27043300200600</a></td><td align="left" style="width:45%;">23206 56TH AVE W, MOUNTLAKE TERRACE, WA 98043-4716</td>
                //        </tr>
                //</tbody></table>
                //const table = await page.waitForSelector('table#mGrid');
                const parcelCell = await page.waitForSelector('table#mGrid td:first-child a')

                await parcelCell.click();

                await page.waitForSelector('::-p-text("Property Account Summary")');

                const page2 = await this.getPageResults(page);
                await this.writeOutPath(key, pn, page2.url, page2.html);
            } catch (err) {
                console.error("Something went wrong while crawling houseinfo: ", err);
                const screenshotPath = this.getScreenShotFileName(key, pn);
                console.error("Saving a screenshot: ", screenshotPath);
                await page.screenshot({ path: screenshotPath });
            }

            await browser.close();
        })();
    }

    createStartUrlPair(location) {
        const streetAddress = location.address.split(",")[0];
        const encodedKey = encodeURI(streetAddress);
        return [
            encodedKey,
            `https://www.snoco.org/proptax/search.aspx?address=${encodedKey}`
        ];
    }
}

new HouseInfoCrawler().run();
