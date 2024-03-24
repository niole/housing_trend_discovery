import fs from 'node:fs';
import { mkdir, readFile } from 'node:fs/promises';
import puppeteer from 'puppeteer';

/**
 * Extend this in order to crawl pages
 * This handles saving urls files to the right location
 */
class Base {
    constructor(sessionId) {
        // required, name of the scraper
        this.name = "base";

        // optional, what session to generate for
        this.sessionId = sessionId;
    }

    /**
     * Override
     *
     *This is the first function that scrapy calls with the urls you provided it.

     *Input
     *    key: the key that identifies the home being scraped

     *Response
     *    A scraper function that parses the response object from scrapy and saves the html file
     *    contents to the file system. The out path will be namespaced by the key
    **/
    parse(key, startUrl) {
        console.log("Not implemented: Crawling ", key, " ", startUrl);
        //(async () => {
        //    const browser = await puppeteer.launch();
        //    const page = await browser.newPage();

        //    await page.goto(startUrl);

        //    const url = await page.url();
        //    const html = await page.content();
        //    this.writeOutPath(key, 1, url, html)

        //    await browser.close();
        //})();
    }

    /**
     * Override
     * Input
     *     element from scraper input json  list

     * Returns
     *     (key, url), where key identifies the house being scraped and will be used later to identify
     *     home entries in the database, and url which is the start url to begin scraping from
     * */
    createStartUrlPair(address) {
        return [address.address, "fakeurl.com"]
    }

    async getPageResults(page) {
        const url = await page.url();
        const html = await page.content();

        return { url, html };
    }

    async createStartUrlPairs() {
        try {
            const data = await readFile(this.getInputsBasePath(), 'utf8');
            const addresses = JSON.parse(data);
            return addresses.map(a => {
                const pair = this.createStartUrlPair(a);
                return [...pair, a];
            });
        } catch (err) {
            console.error('Failed to read input data: ', err)
            throw err;
        }
    }

    /**
    Writes the found html files to the file system for parsing.

    Input
        key: the key that identifies the home being scraped
        pn: the page number, first page will be 1, etc...
        url: the url of the page
        html: the html contents of the page
    **/
    writeOutPath(key, pn, url, html) {
        this.writeToPath(`${this.getOutBasePath()}/${key}/page_${pn}.html`, html);
        this.writeToPath(`${this.getOutBasePath()}/${key}/urls/url_${pn}.txt`, url);
    }

    saveInputJson(key, inputJson) {
        this.writeToPath(`${this.getInputsDirPath(key)}/inputs.json`, JSON.stringify(inputJson));
    }

    run() {
        this.createStartUrlPairs()
            .then(startUrls => {
                startUrls.forEach(([key, url, inputJson]) => {
                    this.initDirs(key)
                        .then(() => {
                            this.saveInputJson(key, inputJson)
                            this.parse(key, url);
                        });
                });
            })
            .catch(e => {
                console.error('Failed to start crawler: ', e);
            });
    }

    getSessionId() {
        if (!this.sessionId) {
            const time = Date.now();
            this.sessionId = `${this.name}-${time}`;
        }
        return this.sessionId;
    }

    writeToPath(path, content) {
        fs.writeFile(path, content, err => {
            if (err) {
                console.error(err);
            }
        });
    }

    getOutBasePath() {
        return `./data/${this.getSessionId()}`;
    }

    getInputsBasePath() {
        return `./inputs/${this.name}.json`;
    }

    getScreenShotFileName(key, pn) {
        return `${this.getScreenshotsDirPath(key)}/${pn}.png`;
    }

    getScreenshotsDirPath(key) {
        return `${this.getOutBasePath()}/${key}/screenshots`;
    }

    getInputsDirPath(key) {
        return `${this.getOutBasePath()}/${key}/inputs`;
    }

    async initDirs(key) {
        await mkdir(this.getOutBasePath(), { recursive: true });
        await mkdir(`${this.getOutBasePath()}/${key}`, { recursive: true });
        await mkdir(this.getScreenshotsDirPath(key), { recursive: true });
        await mkdir(this.getInputsDirPath(key), { recursive: true });
        const createDir = await mkdir(`${this.getOutBasePath()}/${key}/urls`, { recursive: true });
        console.log(`created ${createDir}`);
    }
}

export default Base;
