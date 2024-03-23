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
            const page = await browser.newPage();

            await page.goto(startUrl);

            const page1 = await this.getPageResults(page);
            await this.writeOutPath(key, 1, page1.url, page1.html);

            //<table cellspacing="0" rules="all" border="1" id="mGrid" style="width:100%;border-collapse:collapse;">
            //    <tbody><tr class="GridHeader">
            //            <th align="left" scope="col">Parcel Number</th><th align="left" scope="col">Location Address</th>
            //            </tr><tr>
            //            <td align="left" style="width:10%;"><a href="ParcelInfo.aspx?parcel_number=27043300200600">27043300200600</a></td><td align="left" style="width:45%;">23206 56TH AVE W, MOUNTLAKE TERRACE, WA 98043-4716</td>
            //        </tr>
            //</tbody></table>
            //const table = await page.waitForSelector('table#mGrid');
            const parcelCell = await page.waitForSelector('table#mGrid td:first-child a')

            console.log('parcelCell', parcelCell);

            await parcelCell.click();

            await page.waitForSelector('::-p-text("Property Account Summary")');

            // await page.screenshot({path: '/home/niole/secondpage.png'});

            const page2 = await this.getPageResults(page);
            await this.writeOutPath(key, 2, page2.url, page2.html);

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

console.log(process.argv);
new HouseInfoCrawler().run();
