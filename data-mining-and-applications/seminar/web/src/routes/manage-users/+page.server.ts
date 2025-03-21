import { PUBLIC_BASE_URL } from '$env/static/public';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, url }) => {
	const filterid = url.searchParams.get('filterid')?.toString();

	const searchParams = new URLSearchParams({
		limit: '10'
	});

	if (filterid) {
		searchParams.append('filterid', filterid);
	}
	const response = await fetch(new URL(`/api/v1/customers?${searchParams}`, PUBLIC_BASE_URL));
	if (response.ok) {
		return {
			customers: await response.json()
		};
	}
};

export const actions: Actions = {
	default: async ({ request }) => {
		const formData = await request.formData();
		const filterid = formData.get('filterid')?.toString().split(',');
		if (!filterid) {
			return;
		}
	}
};
