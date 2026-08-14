<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import { authUserStore } from '@/stores/authUserStore';

const userStore = authUserStore();

const requests = ref([]);
const loading = ref(true);
const submitting = ref(false);
const error = ref(null);
const success = ref(null);
const uploadRequestId = ref(null);
const docFile = ref(null);
const docType = ref('business_registration_document');

const payoutMethods = ref([]);
const payoutConfig = ref(null);
const payoutError = ref(null);
const payoutSuccess = ref(null);
const payoutForm = ref({
  method_type: 'bank',
  display_name: '',
  account_identifier: '',
  bank_name: '',
  account_holder: '',
  is_primary: false,
});

const form = ref({
  display_name: '',
  description: '',
  industry: '',
  size_min: null,
  size_max: null,
  website: '',
  domain: '',
  registration_country: 'VN',
  registration_authority: 'NATIONAL',
  registration_type: 'LLC',
  registration_number_raw: '',
  tax_id: '',
  vat_number: '',
  signer_full_name: '',
  primary_document_language: 'en',
  company_email: '',
  address_line: '',
  city: '',
  branch_country: 'VN',
  terms_version: 'hiring-rights-kyc-v1',
});

const docTypes = [
  'business_registration_document',
  'tax_registration_document',
  'authorization_evidence',
  'identity_document',
  'document_translation',
];

const REQUIRED_FIELDS = [
  ['display_name', 'Company display name'],
  ['registration_country', 'Registration country'],
  ['registration_type', 'Registration type'],
  ['registration_number_raw', 'Registration number'],
  ['signer_full_name', 'Signer full name'],
  ['primary_document_language', 'Document language'],
  ['company_email', 'Company email'],
];

function formatApiError(err, fallback = 'Request failed') {
  const status = err?.response?.status;
  const detail = err?.response?.data?.detail;
  let message = fallback;

  if (typeof detail === 'string') {
    message = detail;
  } else if (Array.isArray(detail)) {
    message = detail
      .map((item) => {
        const loc = Array.isArray(item?.loc)
          ? item.loc.filter((p) => p !== 'body').join('.')
          : '';
        const msg = item?.msg || JSON.stringify(item);
        return loc ? `${loc}: ${msg}` : msg;
      })
      .join('; ');
  } else if (detail != null) {
    message = JSON.stringify(detail);
  } else if (err?.message) {
    message = err.message;
  }

  if (status === 403 && /token has expired/i.test(message)) {
    message =
      'Session expired (Token has expired). Log out and log in again, then resubmit.';
  } else if (status === 403 && /csrf/i.test(message)) {
    message = 'CSRF validation failed. Refresh the page, then try again.';
  }

  const prefixed = status ? `[${status}] ${message}` : message;
  console.error('[Settings]', prefixed, err?.response?.data || err);
  return prefixed;
}

function validateRequired() {
  const missing = REQUIRED_FIELDS.filter(
    ([key]) => !String(form.value[key] ?? '').trim()
  ).map(([, label]) => label);
  if (missing.length) {
    return `Missing required fields: ${missing.join(', ')}`;
  }
  return null;
}

async function loadPayout() {
  try {
    const [methodsRes, configRes] = await Promise.all([
      axios.get('/api/marketplace/me/payment-methods'),
      axios.get('/api/marketplace/me/payout-config'),
    ]);
    payoutMethods.value = methodsRes.data || [];
    payoutConfig.value = configRes.data;
  } catch (e) {
    payoutError.value = formatApiError(e, 'Failed to load payout settings');
  }
}

async function addPayoutMethod() {
  payoutError.value = null;
  payoutSuccess.value = null;
  if (!payoutForm.value.display_name.trim() || !payoutForm.value.account_identifier.trim()) {
    payoutError.value = 'Display name and account identifier are required.';
    return;
  }
  try {
    await axios.post('/api/marketplace/me/payment-methods', {
      method_type: payoutForm.value.method_type,
      display_name: payoutForm.value.display_name,
      account_identifier: payoutForm.value.account_identifier,
      bank_name: payoutForm.value.bank_name || null,
      account_holder: payoutForm.value.account_holder || null,
      is_primary: payoutForm.value.is_primary,
    });
    payoutForm.value = {
      method_type: 'bank',
      display_name: '',
      account_identifier: '',
      bank_name: '',
      account_holder: '',
      is_primary: false,
    };
    payoutSuccess.value = 'Payout method added.';
    await loadPayout();
  } catch (e) {
    payoutError.value = formatApiError(e, 'Cannot add payout method');
  }
}

async function setPrimary(id) {
  payoutError.value = null;
  try {
    await axios.patch(`/api/marketplace/me/payment-methods/${id}`, { is_primary: true });
    payoutSuccess.value = 'Primary payout updated.';
    await loadPayout();
  } catch (e) {
    payoutError.value = formatApiError(e, 'Cannot set primary');
  }
}

async function deactivateMethod(id) {
  payoutError.value = null;
  try {
    await axios.patch(`/api/marketplace/me/payment-methods/${id}`, { is_active: false });
    payoutSuccess.value = 'Method deactivated.';
    await loadPayout();
  } catch (e) {
    payoutError.value = formatApiError(e, 'Cannot deactivate');
  }
}

async function deleteMethod(id) {
  payoutError.value = null;
  try {
    await axios.delete(`/api/marketplace/me/payment-methods/${id}`);
    payoutSuccess.value = 'Method deleted.';
    await loadPayout();
  } catch (e) {
    payoutError.value = formatApiError(e, 'Cannot delete');
  }
}

async function loadRequests() {
  loading.value = true;
  try {
    const { data } = await axios.get('/api/job-market/me/hiring-rights-requests');
    requests.value = data || [];
    if (requests.value.length && !uploadRequestId.value) {
      uploadRequestId.value = requests.value[0].id;
    }
  } catch (e) {
    error.value = formatApiError(e, 'Failed to load requests');
  } finally {
    loading.value = false;
  }
}

async function submitKyc() {
  submitting.value = true;
  error.value = null;
  success.value = null;

  const localErr = validateRequired();
  if (localErr) {
    error.value = localErr;
    submitting.value = false;
    return;
  }

  try {
    const email =
      form.value.company_email?.trim() ||
      (await axios.get('/api/users/me')).data.email;
    const payload = {
      ...form.value,
      company_email: email,
      size_min:
        form.value.size_min === '' || form.value.size_min == null
          ? null
          : Number(form.value.size_min),
      size_max:
        form.value.size_max === '' || form.value.size_max == null
          ? null
          : Number(form.value.size_max),
    };
    const { data } = await axios.post('/api/job-market/me/hiring-rights-requests', payload);
    success.value = `Request #${data.id} submitted. Confirm company email, then upload documents.`;
    uploadRequestId.value = data.id;
    if (data.warnings?.length) {
      success.value += ` Warnings: ${data.warnings.map((w) => w.code).join(', ')}`;
    }
    await loadRequests();
  } catch (e) {
    error.value = formatApiError(e, 'Submit failed');
  } finally {
    submitting.value = false;
  }
}

async function uploadDoc() {
  if (!uploadRequestId.value || !docFile.value) {
    error.value = 'Select a request and choose a file before upload.';
    return;
  }
  error.value = null;
  const fd = new FormData();
  fd.append('doc_type', docType.value);
  fd.append('file', docFile.value);
  try {
    await axios.post(
      `/api/job-market/me/hiring-rights-requests/${uploadRequestId.value}/documents`,
      fd
    );
    success.value = 'Document uploaded.';
    docFile.value = null;
  } catch (e) {
    error.value = formatApiError(e, 'Upload failed');
  }
}

async function resendConfirm(id) {
  try {
    await axios.post(`/api/job-market/me/hiring-rights-requests/${id}/resend-confirm`);
    success.value = 'Confirmation email resent.';
  } catch (e) {
    error.value = formatApiError(e, 'Resend failed');
  }
}

function onFileChange(e) {
  docFile.value = e.target.files?.[0] || null;
}

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/users/me');
    form.value.company_email = data.email || '';
    if (!form.value.signer_full_name) {
      form.value.signer_full_name = data.username || '';
    }
    userStore.setAccountKind(data.account_kind || 'personal', data.company_id ?? null);
  } catch (e) {
    error.value = formatApiError(
      e,
      'Cannot load session. Log in again before submitting KYC.'
    );
  }
  await Promise.all([loadRequests(), loadPayout()]);
});
</script>

<template>
  <div class="ml-20 min-h-screen px-10 py-10 max-w-2xl">
    <h1 class="text-3xl font-bold mb-2">Settings</h1>
    <p class="text-gray-600 mb-8 text-sm">
      Signed in as {{ userStore.authUsername }}
      <span v-if="userStore.roles?.length">
        · roles: {{ userStore.roles.join(', ') }}
      </span>
      <span v-if="userStore.accountKind">
        · account: {{ userStore.accountKind }}
      </span>
    </p>

    <section class="border border-gray-200 rounded-2xl p-6 mb-8">
      <h2 class="text-lg font-semibold mb-2">Seller payout</h2>
      <p class="text-sm text-gray-600 mb-3">
        Bank / e-wallet destinations for marketplace sales. No internal wallet.
      </p>
      <p v-if="payoutConfig" class="text-sm mb-3">
        Platform commission:
        <strong>{{ payoutConfig.commission_percent }}%</strong>
        <span class="text-gray-500"> — {{ payoutConfig.estimate_note }}</span>
      </p>
      <p v-if="payoutError" class="text-red-600 text-sm mb-2">{{ payoutError }}</p>
      <p v-if="payoutSuccess" class="text-green-700 text-sm mb-2">{{ payoutSuccess }}</p>

      <ul class="space-y-2 text-sm mb-4">
        <li
          v-for="m in payoutMethods"
          :key="m.id"
          class="border rounded-xl p-3 flex flex-col gap-1"
        >
          <div class="font-medium">
            {{ m.display_name }}
            <span
              v-if="m.is_primary"
              class="ml-2 text-xs px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800"
            >primary</span>
            <span v-if="!m.is_active" class="ml-2 text-xs text-gray-500">(inactive)</span>
          </div>
          <div class="text-gray-600">
            {{ m.method_type }} · {{ m.account_identifier }}
            <span v-if="m.bank_name"> · {{ m.bank_name }}</span>
            <span v-if="m.account_holder"> · {{ m.account_holder }}</span>
          </div>
          <div class="flex gap-2 mt-1">
            <button
              v-if="m.is_active && !m.is_primary"
              type="button"
              class="underline text-xs"
              @click="setPrimary(m.id)"
            >
              Set primary
            </button>
            <button
              v-if="m.is_active"
              type="button"
              class="underline text-xs"
              @click="deactivateMethod(m.id)"
            >
              Deactivate
            </button>
            <button type="button" class="underline text-xs text-red-600" @click="deleteMethod(m.id)">
              Delete
            </button>
          </div>
        </li>
        <li v-if="!payoutMethods.length" class="text-gray-500">No payout methods yet.</li>
      </ul>

      <div class="grid gap-2 text-sm">
        <select v-model="payoutForm.method_type" class="border rounded-xl px-3 py-2">
          <option value="bank">Bank</option>
          <option value="e_wallet">E-wallet</option>
        </select>
        <input v-model="payoutForm.display_name" placeholder="Display name *" class="border rounded-xl px-3 py-2" />
        <input v-model="payoutForm.account_identifier" placeholder="Account / wallet id *" class="border rounded-xl px-3 py-2" />
        <input v-model="payoutForm.bank_name" placeholder="Bank name (optional)" class="border rounded-xl px-3 py-2" />
        <input v-model="payoutForm.account_holder" placeholder="Account holder (optional)" class="border rounded-xl px-3 py-2" />
        <label class="flex items-center gap-2 text-xs">
          <input v-model="payoutForm.is_primary" type="checkbox" />
          Set as primary
        </label>
        <button type="button" class="px-4 py-2 rounded-full bg-black text-white w-fit" @click="addPayoutMethod">
          Add payout method
        </button>
      </div>
    </section>

    <section
      v-if="userStore.accountKind === 'organization'"
      class="border border-gray-200 rounded-2xl p-6 mb-8"
    >
      <h2 class="text-lg font-semibold mb-2">Hiring rights</h2>
      <p class="text-sm text-gray-600">
        This account is an organization (company_id={{ userStore.companyId }}).
        Manage the company profile from your profile page.
      </p>
    </section>

    <section v-else class="border border-gray-200 rounded-2xl p-6 mb-8">
      <h2 class="text-lg font-semibold mb-2">Request hiring rights</h2>
      <p class="text-sm text-gray-600 mb-4">
        Submit company KYC. Company email must match your verified account email.
      </p>

      <p v-if="error" class="text-red-600 text-sm mb-3 whitespace-pre-wrap break-words bg-red-50 border border-red-200 rounded-xl px-3 py-2">
        {{ error }}
      </p>
      <p v-if="success" class="text-green-700 text-sm mb-3">{{ success }}</p>

      <div class="grid gap-3 text-sm">
        <input v-model="form.display_name" placeholder="Company display name *" class="border rounded-xl px-3 py-2" />
        <textarea v-model="form.description" placeholder="Description" rows="3" class="border rounded-xl px-3 py-2" />
        <input v-model="form.industry" placeholder="Industry" class="border rounded-xl px-3 py-2" />
        <div class="flex gap-2">
          <input v-model="form.size_min" type="number" placeholder="Size min" class="border rounded-xl px-3 py-2 w-1/2" />
          <input v-model="form.size_max" type="number" placeholder="Size max" class="border rounded-xl px-3 py-2 w-1/2" />
        </div>
        <input v-model="form.website" placeholder="Website" class="border rounded-xl px-3 py-2" />
        <input v-model="form.domain" placeholder="Domain" class="border rounded-xl px-3 py-2" />
        <input v-model="form.registration_country" placeholder="Registration country *" class="border rounded-xl px-3 py-2" />
        <input v-model="form.registration_authority" placeholder="Authority (default NATIONAL)" class="border rounded-xl px-3 py-2" />
        <input v-model="form.registration_type" placeholder="Registration type *" class="border rounded-xl px-3 py-2" />
        <input v-model="form.registration_number_raw" placeholder="Registration number *" class="border rounded-xl px-3 py-2" />
        <input v-model="form.tax_id" placeholder="Tax ID (optional)" class="border rounded-xl px-3 py-2" />
        <input v-model="form.vat_number" placeholder="VAT (optional)" class="border rounded-xl px-3 py-2" />
        <input v-model="form.address_line" placeholder="Primary address" class="border rounded-xl px-3 py-2" />
        <input v-model="form.city" placeholder="City" class="border rounded-xl px-3 py-2" />
        <input v-model="form.signer_full_name" placeholder="Signer full name *" class="border rounded-xl px-3 py-2" />
        <input v-model="form.primary_document_language" placeholder="Document language (en, …) *" class="border rounded-xl px-3 py-2" />
        <input v-model="form.company_email" placeholder="Company email (= account email) *" class="border rounded-xl px-3 py-2" />
      </div>

      <button
        type="button"
        class="mt-4 px-5 py-2 rounded-full bg-black text-white disabled:opacity-50"
        :disabled="submitting"
        @click="submitKyc"
      >
        {{ submitting ? 'Submitting…' : 'Submit KYC request' }}
      </button>

      <div class="mt-8 border-t pt-4">
        <h3 class="font-semibold mb-2">Upload KYC documents</h3>
        <select v-model="uploadRequestId" class="border rounded-xl px-3 py-2 mb-2 w-full">
          <option :value="null" disabled>Select request</option>
          <option v-for="r in requests" :key="r.id" :value="r.id">
            #{{ r.id }} — {{ r.status }}
            {{ r.company_email_confirmed_at ? '(email OK)' : '(confirm email)' }}
          </option>
        </select>
        <select v-model="docType" class="border rounded-xl px-3 py-2 mb-2 w-full">
          <option v-for="t in docTypes" :key="t" :value="t">{{ t }}</option>
        </select>
        <input type="file" accept=".pdf,.jpg,.jpeg,.png" class="mb-2" @change="onFileChange" />
        <button type="button" class="px-4 py-2 rounded-full border" @click="uploadDoc">
          Upload document
        </button>
      </div>
    </section>

    <section class="border border-gray-200 rounded-2xl p-6">
      <h2 class="text-lg font-semibold mb-3">My KYC requests</h2>
      <p v-if="loading" class="text-sm text-gray-500">Loading…</p>
      <ul v-else class="space-y-3 text-sm">
        <li v-for="r in requests" :key="r.id" class="border rounded-xl p-3">
          <div class="font-medium">#{{ r.id }} · {{ r.status }}</div>
          <div class="text-gray-600">company_id={{ r.company_id }} · {{ r.company_email }}</div>
          <div v-if="!r.company_email_confirmed_at" class="mt-2">
            <button type="button" class="underline" @click="resendConfirm(r.id)">
              Resend confirmation email
            </button>
          </div>
          <div v-if="r.rejection_reason" class="text-red-600 mt-1">{{ r.rejection_reason }}</div>
          <div v-if="r.admin_note" class="text-amber-700 mt-1">Admin: {{ r.admin_note }}</div>
        </li>
        <li v-if="!requests.length" class="text-gray-500">No requests yet.</li>
      </ul>
    </section>
  </div>
</template>
