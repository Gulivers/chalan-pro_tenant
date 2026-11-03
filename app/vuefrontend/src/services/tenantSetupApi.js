import axios from 'axios';

export async function fetchTenantSetup() {
  const { data } = await axios.get('/api/tenant-setup/');
  return data;
}

export async function patchTenantSetup(payload) {
  const { data } = await axios.patch('/api/tenant-setup/', payload);
  return data;
}
