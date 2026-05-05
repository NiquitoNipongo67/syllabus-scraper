from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time, json

options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get('https://coursecatalogue.uva.nl/en/programmes/2025/1/5248')
time.sleep(8)

buttons = driver.find_elements('tag name', 'button')
for btn in buttons:
    if 'shared' in btn.text.lower():
        driver.execute_script('arguments[0].click();', btn)
        time.sleep(4)
        break

logs = driver.get_log('performance')
for log in logs:
    try:
        msg = json.loads(log['message'])
        method = msg.get('message', {}).get('method', '')
        if method == 'Network.requestWillBeSent':
            url = msg['message']['params']['request']['url']
            if 'graphql' in url:
                body = msg['message']['params']['request'].get('postData', '')
                if body:
                    print('FULL BODY:', body)
                    print()
    except Exception:
        pass

driver.quit()