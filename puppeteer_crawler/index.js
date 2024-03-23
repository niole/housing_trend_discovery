import puppeteer from 'puppeteer';

(async () => {
    // Launch the browser and open a new blank page
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    // go to page, download html
    // click on button to go to next page
    // download html

    // Navigate the page to a URL
    await page.goto('https://developer.chrome.com/');

    const url = await page.url();
    const contents = await page.content();

    console.log(url);
    // console.log(contents);

    await browser.close();
})();
