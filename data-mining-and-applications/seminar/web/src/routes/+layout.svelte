<script lang="ts">
	import '../app.css';
	let { children } = $props();

	import CircleUserRound from 'lucide-svelte/icons/circle-user-round';

	const navigations: {
		href: string;
		display: string;
	}[] = [
		{ href: '/', display: 'Dashboard' },
		{ href: '/analytics', display: 'Analytics' },
		{ href: '/details', display: 'Details' },
		{ href: '/manage-users', display: 'Manage users' }
	];
</script>

<svelte:head>
	<title>Customers Analyzer</title>
	<meta name="description" content="This is a clustering model demo of group 4 CS313.P23" />
</svelte:head>

<div
	id="main"
	class="h-screen w-screen overflow-clip bg-linear-to-br from-purple-300 to-pink-300 px-32 py-8"
>
	<div class="flex h-full w-full flex-col gap-4">
		<div
			id="appbar"
			class="mx-auto flex h-3/32 w-3/4 flex-row justify-between rounded-md border-2 border-white/50 bg-white/40 shadow-md backdrop-blur-md"
		>
			<h1 class="ml-8 flex h-full items-center text-lg font-semibold">Customers Analyzer</h1>
			<form method="post" class="flex aspect-square h-full items-center justify-center">
				<button><CircleUserRound size="32"></CircleUserRound></button>
			</form>
		</div>
		<div class="flex h-full w-full flex-row gap-4">
			<div
				id="sidebar"
				class="hidden h-full w-1/4 flex-col rounded-md border-2 border-white/50 bg-white/40 px-8 py-6 shadow-md backdrop-blur-md md:flex"
			>
				{#each navigations as navigation (navigation.href)}
					<a
						href={navigation.href}
						class="flex h-1/16 w-full rounded-md px-4 duration-150 ease-in hover:bg-white/40 hover:shadow-md hover:backdrop-blur-md"
						><span class="my-auto mr-auto flex h-fit w-fit">{navigation.display}</span></a
					>
				{/each}
			</div>
			<div
				class="flex h-full w-full overflow-y-auto rounded-md border-2 border-white/50 bg-white/40 px-12 py-6 shadow-md backdrop-blur-md"
			>
				{@render children()}
			</div>
		</div>
	</div>
</div>
