<script lang="ts">
	import type { PageProps } from './$types';
	import Chart from 'chart.js/auto';

	let { data }: PageProps = $props();
	const analyticsData = data.analyticsData;

	let analyticsChart = $state<HTMLCanvasElement>();

	$effect(() => {
		new Chart(analyticsChart!, {
			type: 'scatter',
			data: analyticsData
		});
	});
</script>

<div class="flex h-full w-full items-center justify-center">
	<div
		class="h-fit w-256 rounded-md border-2 border-white/50 bg-white/40 shadow-md backdrop-blur-md"
	>
		<canvas bind:this={analyticsChart}></canvas>
	</div>
</div>
