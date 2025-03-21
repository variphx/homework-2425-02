import { PUBLIC_BASE_URL } from '$env/static/public';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const response = await fetch(new URL('/api/v1/analytics', PUBLIC_BASE_URL));
	if (response.ok) {
		return {
			analyticsData: await response.json()
		};
	}
};
