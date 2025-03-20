import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	const analyticsData = {
		datasets: [
			{
				label: 'Cluster A',
				data: [
					{
						x: -10,
						y: 0
					},
					{
						x: 0,
						y: 10
					},
					{
						x: 10,
						y: 5
					},
					{
						x: 0.5,
						y: 5.5
					}
				]
			}
		]
	};

	return { analyticsData };
};
