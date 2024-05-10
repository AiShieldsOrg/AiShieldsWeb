//if content falls behind a paywall or authentication wall, do not use

const puppeteer = require('puppeteer')
const fs = require('fs')

const link = 'https://www.google.com'

const scrapeData = async(link) =>{
    const browser = await puppeteer.launch({headless: true})
    const page = await browser.newPage()

    await page.goto(link)

    await page.type('textarea', process.argv[2], {delay:100})

    await page.keyboard.press('Enter', {delay:100})

    await page.waitForNavigation();

    await page.screenshot({path: 'google1.png'}, {delay: 100})
    
    const data = await page.evaluate(()=>{
        const search = document.querySelectorAll('a')
        
        
        const urls = Array.from(search).map(v => v.href)
        return urls
    })
     
    await browser.close()

    const filteredData = data.filter(item => !item.includes("google"))

    //this is needed to collect the links in the python script
    filteredData.forEach((element) =>{
        console.log(element)
    })


    
    return filteredData;

    //console.log(data)
    
}

scrapeData(link)

