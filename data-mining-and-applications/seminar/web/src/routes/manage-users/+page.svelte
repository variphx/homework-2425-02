<script lang="ts">
	import Search from 'lucide-svelte/icons/search';
	import Plus from 'lucide-svelte/icons/plus';
	import RefreshCcw from 'lucide-svelte/icons/refresh-ccw';
	import type { PageProps } from './$types';

	interface Customer {
		id: number;
		name: string;
		age: number;
		education: string;
		sex: 'Male' | 'Female';
		income: string;
		settlement: 'Small city' | 'Mid-sized city' | 'Big city';
	}

	let { data }: PageProps = $props();
	const customers = data.customers;

	let showCustomerAddForm = $state(false);
</script>

<div class="z-0 flex w-full flex-col gap-8">
	<div class="flex h-1/16 w-full flex-row items-center gap-2">
		<form method="get" class="flex h-full w-3/4 items-center gap-2">
			<input
				name="user-id"
				type="tel"
				class="h-full w-full rounded-md border-2 border-white/50 bg-white/40 shadow-md backdrop-blur-md"
				placeholder="Input the ID of the users you want to search for separated by comma"
			/>
			<button
				type="submit"
				title="Search for user(s)"
				class="flex aspect-square h-10 items-center justify-center rounded-md duration-150 ease-in hover:bg-white/40 hover:shadow-md hover:backdrop-blur-md"
			>
				<Search />
			</button>
		</form>
		<form class="flex h-fit w-fit">
			<button
				onclick={() => (showCustomerAddForm = !showCustomerAddForm)}
				type="button"
				title="Add user(s)"
				class="flex aspect-square h-10 items-center justify-center rounded-md duration-150 ease-in hover:bg-white/40 hover:shadow-md hover:backdrop-blur-md"
			>
				<Plus />
			</button>
		</form>
		<form action="" class="flex h-fit w-fit">
			<button
				type="button"
				title="Refresh clustering"
				class="flex aspect-square h-10 items-center justify-center rounded-md duration-150 ease-in hover:bg-white/40 hover:shadow-md hover:backdrop-blur-md"
			>
				<RefreshCcw />
			</button>
		</form>
	</div>

	<div
		class="flex w-full overflow-x-auto rounded-md border-2 border-white/50 bg-white/40 shadow-md backdrop-blur-md"
	>
		<table class="h-full w-full bg-none">
			<thead>
				<tr>
					<th class="p-3 text-left">ID</th>
					<!-- <th class="p-3 text-left">Name</th> -->
					<th class="p-3 text-left">Age</th>
					<th class="p-3 text-left">Sex</th>
					<th class="p-3 text-left">Education</th>
					<th class="p-3 text-left">Income</th>
					<th class="p-3 text-left">Settlement size</th>
				</tr>
			</thead>
			<tbody>
				{#each customers as customer, index (customer.rowid)}
					<tr>
						<td class="border border-white p-3 {index % 2 == 0 ? 'bg-white/40' : ''}"
							>{customer.rowid}</td
						>
						<!-- <td class="border border-white p-3 {index % 2 == 0 ? 'bg-white/40' : ''}"
							>{customer.name}</td
						> -->
						<td class="border border-white p-3 {index % 2 == 0 ? 'bg-white/40' : ''}"
							>{customer.age}</td
						>
						<td class="border border-white p-3 {index % 2 == 0 ? 'bg-white/40' : ''}"
							>{customer.sex}</td
						>
						<td class="border border-white p-3 {index % 2 == 0 ? 'bg-white/40' : ''}"
							>{customer.education}</td
						>
						<td class="border border-white p-3 {index % 2 == 0 ? 'bg-white/40' : ''}"
							>{customer.income}</td
						>
						<td class="border border-white p-3 {index % 2 == 0 ? 'bg-white/40' : ''}"
							>{customer.settlement_size}</td
						>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>

{#if showCustomerAddForm}
	<div
		class="absolute inset-0 z-10 m-auto mx-auto flex h-3/4 w-3/4 rounded-md border-2 border-white/50 bg-white/40 shadow-md backdrop-blur-md"
	></div>
{/if}
