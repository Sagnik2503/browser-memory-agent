const BACKEND_URL = 'http://localhost:8000/ingest';

let lastActiveTab = null;

async function sendEvent(eventData) {
  try {
    await fetch(BACKEND_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(eventData),
    });
  } catch {
  }
}

async function getTabInfo(tabId) {
  try {
    const tab = await chrome.tabs.get(tabId);
    return {
      url: tab.url || '',
      title: tab.title || '',
      tab_id: tab.id,
    };
  } catch {
    return null;
  }
}

//runs when user switches the tab
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  const now = Date.now();
  const { tabId } = activeInfo;

  if (lastActiveTab) {
    const dwellDelta = now - lastActiveTab.timestamp;
    await sendEvent({
      event_type: 'tab_inactive',
      url: lastActiveTab.url,
      title: lastActiveTab.title,
      tab_id: lastActiveTab.tabId,
      timestamp: now,
      dwell_delta: dwellDelta,
    });
  }

  const tabInfo = await getTabInfo(tabId);
  if (!tabInfo) return;

  await sendEvent({
    event_type: 'tab_active',
    url: tabInfo.url,
    title: tabInfo.title,
    tab_id: tabInfo.tab_id,
    timestamp: now,
  });

  lastActiveTab = {
    tabId: tabInfo.tab_id,
    url: tabInfo.url,
    title: tabInfo.title,
    timestamp: now,
  };
});

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status !== 'complete' || !tab.url) return;

  const now = Date.now();

  await sendEvent({
    event_type: 'url_change',
    url: tab.url,
    title: tab.title || '',
    tab_id: tab.id,
    timestamp: now,
  });

  if (lastActiveTab && lastActiveTab.tabId === tabId) {
    lastActiveTab.url = tab.url;
    lastActiveTab.title = tab.title || '';
    lastActiveTab.timestamp = now;
  }
});
