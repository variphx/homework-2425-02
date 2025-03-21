import { error } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { PUBLIC_BASE_URL } from '$env/static/public';

export const load: PageServerLoad = async ({ fetch, url }) => {
	const dataAttribute = url.searchParams.get('data-attribute');
	if (!dataAttribute) {
		const response = await fetch(new URL(`/api/v1/details/age`, PUBLIC_BASE_URL));
		if (response.ok) {
			return await response.json();
		}
	}

	const response = await fetch(new URL(`/api/v1/details/${dataAttribute}`, PUBLIC_BASE_URL));
	if (response.ok) {
		return await response.json();
	}
};

export const actions: Actions = {
	default: async ({ request, fetch }) => {
		const formData = await request.formData();
		const dataAttribute = formData.get('data-attribute')!.toString();

		const response = await fetch(new URL(`/api/v1/details/${dataAttribute}`, PUBLIC_BASE_URL));
		if (response.ok) {
			return await response.json();
		}

		interface Data {
			labels: string[];
			datasets: { label: string; data: number[] | [number, number][] }[];
		}

		switch (dataAttribute) {
			case 'age': {
				const data: Data = {
					labels: ['Cluster A', 'Cluster B', 'Cluster C'],
					datasets: [
						{
							label: 'Age',
							data: [
								[10, 20],
								[20, 30],
								[30, 40]
							]
						}
					]
				};
				return { data, dataAttribute };
			}
			case 'sex': {
				const data: Data = {
					labels: ['Cluster A', 'Cluster B', 'Cluster C'],
					datasets: [
						{
							label: 'Male',
							data: [1, 2, 3]
						},
						{
							label: 'Female',
							data: [3, 2, 1]
						}
					]
				};
				return { data, dataAttribute };
			}
			case 'income': {
				const data: Data = {
					labels: ['Cluster A', 'Cluster B', 'Cluster C'],
					datasets: [
						{
							label: 'Income',
							data: [
								[10, 20],
								[20, 30],
								[30, 40]
							]
						}
					]
				};
				return { data, dataAttribute };
			}
			case 'education': {
				const data: Data = {
					labels: ['Cluster A', 'Cluster B', 'Cluster C'],
					datasets: [
						{
							label: 'Other',
							data: [1, 2, 3]
						},
						{
							label: 'High school',
							data: [3, 2, 1]
						},
						{
							label: 'University',
							data: [1, 2, 3]
						},
						{
							label: 'Graduate school',
							data: [3, 2, 1]
						}
					]
				};
				return { data, dataAttribute };
			}
			case 'marital-status': {
				const data: Data = {
					labels: ['Cluster A', 'Cluster B', 'Cluster C'],
					datasets: [
						{
							label: 'Single',
							data: [1, 2, 3]
						},
						{
							label: 'Non-single',
							data: [3, 2, 1]
						}
					]
				};
				return { data, dataAttribute };
			}
			case 'occupation': {
				const data: Data = {
					labels: ['Cluster A', 'Cluster B', 'Cluster C'],
					datasets: [
						{
							label: 'Unemployed',
							data: [1, 2, 3]
						},
						{
							label: 'Skilled employee',
							data: [3, 2, 1]
						},
						{
							label: 'Highly qualified employee',
							data: [1, 2, 3]
						}
					]
				};
				return { data, dataAttribute };
			}
			case 'settlement-size': {
				const data: Data = {
					labels: ['Cluster A', 'Cluster B', 'Cluster C'],
					datasets: [
						{
							label: 'Small city',
							data: [1, 2, 3]
						},
						{
							label: 'Mid-sized city',
							data: [3, 2, 1]
						},
						{
							label: 'Big city',
							data: [1, 2, 3]
						}
					]
				};
				return { data, dataAttribute };
			}
			default:
				error(422, '');
		}
	}
};
