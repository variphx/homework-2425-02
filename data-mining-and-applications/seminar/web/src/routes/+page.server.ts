import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const totalCustomer = 12345;

	const genderData = {
		labels: ['Male', 'Female'],
		datasets: [
			{
				label: 'Sexes',
				data: [1, 1]
			}
		]
	};

	const maritalStatusData = {
		labels: ['Single', 'Non-single'],
		datasets: [{ label: 'Marital status', data: [1, 1] }]
	};

	const incomeData = {
		labels: ['0-10', '10-20', '20-30', '30-40', '40-50'],
		datasets: [
			{
				label: 'Customers',
				data: [1, 1, 1, 1, 1]
			}
		]
	};

	const settlementData = {
		labels: ['Small city', 'Mid-sized city', 'Big city'],
		datasets: [
			{
				label: 'Settlement size',
				data: [1, 1, 1]
			}
		]
	};

	const occupationData = {
		labels: ['Unemployed', 'Skilled employee', 'Highly qualified employee'],
		datasets: [
			{
				label: 'Occupation',
				data: [1, 1, 1]
			}
		]
	};

	const ageData = {
		labels: ['0-10', '10-20', '20-30', '30-40', '40-50'],
		datasets: [
			{
				label: 'Customers',
				data: [1, 1, 1, 1, 1]
			}
		]
	};

	return {
		totalCustomer,
		genderData,
		maritalStatusData,
		incomeData,
		settlementData,
		occupationData,
		ageData
	};
};
