<script lang="ts">
	import Search from 'lucide-svelte/icons/search';
	import type { PageProps } from './$types';
	import Chart from 'chart.js/auto';

	let { data }: PageProps = $props();
	// const data = form?.data;

	let chart = $state<HTMLCanvasElement>();

	$effect(() => {
		if (!data) {
			return;
		}
		new Chart(chart!, {
			type: 'bar',
			data: data.data as {
				labels: string[];
				datasets: { label: string; data: number[] | [number, number][] }[];
			}
		});
	});

	const dataAtrributeOptions = [
		{ value: 'age', display: 'Age' },
		{ value: 'sex', display: 'Sex' },
		{ value: 'income', display: 'Income' },
		{ value: 'education', display: 'Education' },
		{ value: 'marital-status', display: 'Marital status' },
		{ value: 'occupation', display: 'Occupation' },
		{ value: 'settlement-size', display: 'Settlement size' }
	];
</script>

<div class="flex h-full w-full flex-col items-center justify-between overflow-clip">
	{#if data}
		<div
			class="my-auto flex h-fit w-196 rounded-md border-2 border-white/50 bg-white/40 shadow-md backdrop-blur-md"
		>
			<canvas bind:this={chart}></canvas>
		</div>
	{/if}
	<form data-sveltekit-reload class="flex h-16 flex-col items-center justify-center">
		<div class="flex flex-row items-center justify-center gap-6">
			<select
				name="data-attribute"
				id="data-attribute"
				class="rounded-md border-2 border-white/50 bg-white/40 shadow-md backdrop-blur-md"
				value={data.dataAttribute ? data.dataAttribute : dataAtrributeOptions[0].value}
			>
				{#each dataAtrributeOptions as option (option.value)}
					<option value={option.value}>{option.display}</option>
				{/each}
			</select>
			<button
				type="submit"
				title="Visualize selected data attribute"
				class="flex aspect-square w-8 items-center justify-center rounded-md border-2 border-white/50 bg-white/40 text-center shadow-md backdrop-blur-md"
				><Search></Search></button
			>
		</div>
	</form>
</div>
