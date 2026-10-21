import crypto from 'node:crypto';

export const config = {
  api: {
    bodyParser: false,
  },
};

// In-memory caching for warm function invocations
let cachedAccessToken = null;
let tokenExpiry = 0;
let cachedConversionActionResource = null;

export function resetCache() {
  cachedAccessToken = null;
  tokenExpiry = 0;
  cachedConversionActionResource = null;
}

export async function getRawBody(req) {
  if (req.rawBody) {
    return Buffer.isBuffer(req.rawBody) ? req.rawBody : Buffer.from(req.rawBody);
  }
  if (Buffer.isBuffer(req.body)) {
    return req.body;
  }
  if (typeof req.body === 'string') {
    return Buffer.from(req.body);
  }
  if (req.body && typeof req.body === 'object') {
    return Buffer.from(JSON.stringify(req.body));
  }
  const chunks = [];
  for await (const chunk of req) {
    chunks.push(typeof chunk === 'string' ? Buffer.from(chunk) : chunk);
  }
  return Buffer.concat(chunks);
}

export function verifyTiqetsSignature(rawBody, signatureHeader, secret) {
  if (!secret) {
    if (process.env.NODE_ENV !== 'production' && !signatureHeader) {
      return true;
    }
    return false;
  }
  if (!signatureHeader) return false;

  const cleanedSig = signatureHeader.replace(/^sha256=/, '').trim();
  const expectedHmacHex = crypto
    .createHmac('sha256', secret)
    .update(rawBody)
    .digest('hex');

  const actualHash = crypto.createHash('sha256').update(cleanedSig).digest();
  const expectedHash = crypto.createHash('sha256').update(expectedHmacHex).digest();

  return crypto.timingSafeEqual(actualHash, expectedHash);
}

export function extractClickId(payload) {
  if (!payload || typeof payload !== 'object') return null;

  const tqCampaign = payload.tq_campaign || payload.campaign || '';
  if (typeof tqCampaign === 'string' && tqCampaign.trim()) {
    const trimmed = tqCampaign.trim();

    // 1. Composite tag: --gclid-<value> or --wbraid-<value>
    const match = trimmed.match(/(gclid|wbraid|gbraid)-([a-zA-Z0-9_-]+)/i);
    if (match && match[2]) {
      const type = match[1].toLowerCase();
      const extracted = match[2].split(/--|[&?#]/)[0].trim();
      if (extracted && !/organic|direct|referral|social|banner/i.test(extracted)) {
        return { type, value: extracted };
      }
    }

    // 2. Raw GCLID string matching standard GCLID length & character set (excluding organic / direct keywords)
    if (/^[a-zA-Z0-9_-]{20,}$/.test(trimmed) && !/organic|direct|referral|social|banner/i.test(trimmed)) {
      return { type: 'gclid', value: trimmed };
    }
  }

  // 3. Fallback: Direct payload properties
  for (const type of ['gclid', 'wbraid', 'gbraid']) {
    if (typeof payload[type] === 'string' && payload[type].trim()) {
      const trimmedVal = payload[type].trim();
      if (trimmedVal.length >= 15 && !/organic|direct|referral/i.test(trimmedVal)) {
        return { type, value: trimmedVal };
      }
    }
  }

  // 4. Fallback: subid containing key-value pair
  if (typeof payload.subid === 'string') {
    const subidMatch = payload.subid.match(/(gclid|wbraid|gbraid):([^|?&#]+)/i);
    if (subidMatch && subidMatch[2]) {
      return { type: subidMatch[1].toLowerCase(), value: subidMatch[2].trim() };
    }
  }

  return null;
}

export function extractGclid(payload) {
  const result = extractClickId(payload);
  return result ? result.value : null;
}

export function formatGoogleAdsDateTime(isoString) {
  const date = isoString ? new Date(isoString) : new Date();
  if (isNaN(date.getTime())) {
    const fallbackDate = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    return `${fallbackDate.getUTCFullYear()}-${pad(fallbackDate.getUTCMonth() + 1)}-${pad(fallbackDate.getUTCDate())} ${pad(fallbackDate.getUTCHours())}:${pad(fallbackDate.getUTCMinutes())}:${pad(fallbackDate.getUTCSeconds())}+00:00`;
  }
  const pad = (n) => String(n).padStart(2, '0');
  return `${date.getUTCFullYear()}-${pad(date.getUTCMonth() + 1)}-${pad(date.getUTCDate())} ${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}:${pad(date.getUTCSeconds())}+00:00`;
}

export async function getAccessToken(forceRefresh = false) {
  const now = Date.now();
  if (!forceRefresh && cachedAccessToken && now < tokenExpiry) {
    return cachedAccessToken;
  }

  const clientId = process.env.GOOGLE_ADS_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_ADS_CLIENT_SECRET;
  const refreshToken = process.env.GOOGLE_ADS_REFRESH_TOKEN;

  if (!clientId || !clientSecret || !refreshToken) {
    if (process.env.NODE_ENV === 'test' || process.env.NODE_ENV !== 'production') {
      cachedAccessToken = 'mock-dev-access-token';
      tokenExpiry = now + 3600000;
      return cachedAccessToken;
    }
    throw new Error('Missing Google Ads OAuth credentials');
  }

  const params = new URLSearchParams({
    client_id: clientId,
    client_secret: clientSecret,
    refresh_token: refreshToken,
    grant_type: 'refresh_token'
  });

  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString()
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`OAuth refresh failed (${res.status}): ${errText}`);
  }

  const data = await res.json();
  cachedAccessToken = data.access_token;
  tokenExpiry = now + (((data.expires_in || 3600) - 300) * 1000);
  return cachedAccessToken;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'method_not_allowed' });
  }

  try {
    const rawBodyBuffer = await getRawBody(req);
    const signature = req.headers['x-tiqets-signature'] || req.headers['authorization'];
    const webhookSecret = process.env.TIQETS_WEBHOOK_SECRET;

    if (webhookSecret || signature) {
      if (!verifyTiqetsSignature(rawBodyBuffer, signature, webhookSecret)) {
        return res.status(401).json({ error: 'invalid_signature' });
      }
    }

    let payload;
    try {
      payload = JSON.parse(rawBodyBuffer.toString('utf-8'));
    } catch (e) {
      return res.status(400).json({ error: 'invalid_json' });
    }

    const clickIdObj = extractClickId(payload);
    if (!clickIdObj) {
      return res.status(200).json({ status: 'skipped', reason: 'no_gclid_found' });
    }

    const customerId = (process.env.GOOGLE_ADS_CUSTOMER_ID || '4899321613').replace(/-/g, '');
    const devToken = process.env.GOOGLE_ADS_DEVELOPER_TOKEN || 'WK-A1HREvXxnsvVLsWELNg';
    const actionName = process.env.GOOGLE_ADS_CONVERSION_ACTION_NAME || 'Tiqets Offline Sale';

    let accessToken = await getAccessToken();

    // If conversion action resource name is provided in env, use it directly
    if (process.env.GOOGLE_ADS_CONVERSION_ACTION_ID) {
      cachedConversionActionResource = `customers/${customerId}/conversionActions/${process.env.GOOGLE_ADS_CONVERSION_ACTION_ID}`;
    }

    // Resolve resource name if not cached
    if (!cachedConversionActionResource) {
      try {
        const searchRes = await fetch(`https://googleads.googleapis.com/v17/customers/${customerId}/googleAds:searchStream`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'developer-token': devToken,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            query: `SELECT conversion_action.resource_name FROM conversion_action WHERE conversion_action.name = '${actionName}'`
          })
        });

        if (searchRes.ok) {
          const searchData = await searchRes.json();
          if (Array.isArray(searchData) && searchData[0]?.results?.[0]?.conversionAction?.resourceName) {
            cachedConversionActionResource = searchData[0].results[0].conversionAction.resourceName;
          }
        }
      } catch (err) {
        // Fall back to default resource name if search stream fails
      }
    }

    const conversionActionResource = cachedConversionActionResource || `customers/${customerId}/conversionActions/default_action_id`;
    const conversionDateTime = formatGoogleAdsDateTime(payload.created_at);

    let rawPrice = payload.financials?.total_price;
    if (rawPrice === undefined || rawPrice === null) {
      rawPrice = payload.financials?.commission_amount;
    }
    const conversionValue = Math.round((parseFloat(rawPrice) || 0) * 100) / 100;
    const currencyCode = (payload.financials?.currency || 'EUR').toUpperCase();
    const orderId = payload.order_id || payload.booking_reference || `TQ-${Date.now()}`;
    const validateOnly = Boolean(payload.validateOnly || (req.query && req.query.validateOnly));

    const postUpload = async (token) => {
      const conversionEvent = {
        conversionAction: conversionActionResource,
        conversionDateTime: conversionDateTime,
        conversionValue: conversionValue,
        currencyCode: currencyCode,
        orderId: orderId
      };
      conversionEvent[clickIdObj.type] = clickIdObj.value;

      return fetch(`https://googleads.googleapis.com/v17/customers/${customerId}:uploadClickConversions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'developer-token': devToken,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          customerId: customerId,
          conversions: [conversionEvent],
          partialFailure: true,
          validateOnly: validateOnly
        })
      });
    };

    let uploadRes = await postUpload(accessToken);

    // Handle token expiration / 401 retry once
    if (uploadRes.status === 401) {
      accessToken = await getAccessToken(true);
      uploadRes = await postUpload(accessToken);
    }

    if (uploadRes.status >= 500) {
      return res.status(500).json({ error: 'google_api_unavailable' });
    }

    const uploadData = await uploadRes.json();
    if (!uploadRes.ok) {
      // Check for duplicate conversion error in partial failures or error body
      const isDuplicate = JSON.stringify(uploadData).includes('CLICK_CONVERSION_ALREADY_EXISTS');
      if (isDuplicate) {
        return res.status(200).json({
          status: 'success',
          deduplicated: true,
          order_id: orderId,
          google_response: uploadData
        });
      }
      return res.status(500).json({ error: 'google_api_error', details: uploadData });
    }

    // Check partial failures in 200 response if any
    const isDuplicatePartial = uploadData.partialFailureError && JSON.stringify(uploadData).includes('CLICK_CONVERSION_ALREADY_EXISTS');

    return res.status(200).json({
      success: true,
      deduplicated: Boolean(isDuplicatePartial),
      order_id: orderId,
      gclid: clickIdObj.value,
      click_id_type: clickIdObj.type,
      google_response: uploadData
    });

  } catch (error) {
    return res.status(500).json({ error: 'internal_server_error', message: error.message });
  }
}
