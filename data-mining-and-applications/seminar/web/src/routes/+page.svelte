<script lang="ts">
	import { page } from '$app/state';
	import Chart from 'chart.js/auto';
	import type { PageServerData } from './$types';

	let genderChart = $state<HTMLCanvasElement>();
	let maritalStatusChart = $state<HTMLCanvasElement>();
	let incomeChart = $state<HTMLCanvasElement>();
	let settlementChart = $state<HTMLCanvasElement>();
	let occupationChart = $state<HTMLCanvasElement>();
	let ageChart = $state<HTMLCanvasElement>();

	const {
		totalCustomer,
		genderData,
		maritalStatusData,
		incomeData,
		settlementData,
		occupationData,
		ageData
	} = page.data as PageServerData;

	$effect(() => {
		new Chart(genderChart!, {
			type: 'pie',
			data: genderData,
			options: {
				responsive: true,
				maintainAspectRatio: false
			}
		});
	});

	$effect(() => {
		new Chart(maritalStatusChart!, {
			type: 'bar',
			data: maritalStatusData,
			options: {
				responsive: true,
				maintainAspectRatio: false,
				scales: {
					x: {
						display: false
					}
				}
			}
		});
	});

	$effect(() => {
		new Chart(incomeChart!, {
			type: 'bar',
			data: incomeData,
			options: {
				responsive: true,
				maintainAspectRatio: false,
				scales: {
					x: {
						display: false
					}
				}
			}
		});
	});

	$effect(() => {
		new Chart(settlementChart!, {
			type: 'bar',
			data: settlementData,
			options: {
				responsive: true,
				maintainAspectRatio: false,
				scales: {
					x: {
						display: false
					}
				}
			}
		});
	});

	$effect(() => {
		new Chart(occupationChart!, {
			type: 'bar',
			data: occupationData,
			options: {
				responsive: true,
				maintainAspectRatio: false,
				scales: {
					x: {
						display: false
					}
				}
			}
		});
	});

	$effect(() => {
		new Chart(ageChart!, {
			type: 'bar',
			data: ageData,
			options: {
				responsive: true,
				maintainAspectRatio: false,
				scales: {
					x: {
						display: false
					}
				}
			}
		});
	});
</script>

<div
	class="grid h-full w-full grid-cols-1 grid-rows-[auto_1fr_1fr] gap-4 overflow-clip md:grid-cols-2 lg:grid-cols-3"
>
	<div
		id="total-customers"
		class="col-span-1 flex flex-col items-center justify-center rounded-md border-2 border-white/50 bg-white/40 p-6 text-center shadow-md backdrop-blur-md md:col-span-2 lg:col-span-3"
	>
		<h2 class="text-xl font-semibold">Total Customers</h2>
		<p class="text-3xl font-bold">{totalCustomer.toLocaleString('vi', { useGrouping: true })}</p>
	</div>
	<div
		id="gender-distribution"
		class="flex flex-col items-center justify-between rounded-md border-2 border-white/50 bg-white/40 p-6 shadow-md backdrop-blur-md"
	>
		<h3 class="mb-4 w-full text-lg font-semibold">Gender Distribution</h3>
		<div class="my-auto flex h-48 w-48">
			<canvas bind:this={genderChart}></canvas>
		</div>
	</div>
	<div
		id="martial-status-breakdown"
		class="flex flex-col items-center justify-between rounded-md border-2 border-white/50 bg-white/40 p-6 shadow-md backdrop-blur-md"
	>
		<h3 class="mb-4 w-full text-lg font-semibold">Marital Status Breakdown</h3>
		<div class="my-auto flex h-48 w-48">
			<canvas bind:this={maritalStatusChart}></canvas>
		</div>
	</div>
	<div
		id="income-distribution"
		class="flex flex-col items-center justify-between rounded-md border-2 border-white/50 bg-white/40 p-6 shadow-md backdrop-blur-md"
	>
		<h3 class="mb-4 w-full text-lg font-semibold">Income Distribution</h3>
		<div class="my-auto flex h-48 w-48">
			<canvas bind:this={incomeChart}></canvas>
		</div>
	</div>
	<div
		id="settlement-size"
		class="flex flex-col items-center justify-between rounded-md border-2 border-white/50 bg-white/40 p-6 shadow-md backdrop-blur-md"
	>
		<h3 class="mb-4 flex w-full text-lg font-semibold">Settlement Size</h3>
		<div class="my-auto flex h-48 w-48">
			<canvas bind:this={settlementChart}></canvas>
		</div>
	</div>
	<div
		id="top-occupations"
		class="flex flex-col items-center justify-between rounded-md border-2 border-white/50 bg-white/40 p-6 shadow-md backdrop-blur-md"
	>
		<h3 class="mb-4 flex w-full text-lg font-semibold">Top Occupations</h3>
		<div class="my-auto flex h-48 w-48">
			<canvas bind:this={occupationChart}></canvas>
		</div>
	</div>
	<div
		id="age-distribution"
		class="flex flex-col items-center justify-between rounded-md border-2 border-white/50 bg-white/40 p-6 shadow-md backdrop-blur-md"
	>
		<h3 class="mb-4 flex w-full text-lg font-semibold">Age Distribution</h3>
		<div class="my-auto flex h-48 w-48">
			<canvas bind:this={ageChart}></canvas>
		</div>
	</div>
</div>
