<script>
    import {
        Heading,
        P,
        A,
        Spinner,
        Table,
        TableBody,
        TableBodyCell,
        TableBodyRow,
        TableHead,
        TableHeadCell,
    } from "flowbite-svelte";
    import { selectedSpecies } from "../../lib/stores";
    import { load } from "../../lib/fetch";
    import { debounce } from "../../lib/utils";
    import { onMount } from "svelte";
    import { SearchOutline, ChevronDownOutline } from "flowbite-svelte-icons";

    let species = "";
    let selected = "";
    let isLoading = false;
    let sconable;
    let sconable_columns;
    let exoninfo;
    let cexoninfo;
    let maxVal = null;
    let clickedRows = [];
    let sequence;
    let chunkedSeq;

    function toggleClick(index) {
        clickedRows[index] = !clickedRows[index];
        console.log("clickedRows", clickedRows);
    }

    let suggestions = [];
    let allSpecies = [];
    let selectSuggestions = [];
    let selectOptions = [];

    const debouncedFetchData = debounce(fetchData, 300);
    selectedSpecies.subscribe((value) => {
        species = value;
        console.log(value);
        if (species) {
            debouncedFetchData();
        }
    });
    async function fetchData() {
        isLoading = true;
        try {
            const [speciesData, metaData] = await Promise.all([
                load(`sconable_genes?species=${species}&ensemble_rev=109`),
                load("meta/dataset"),
            ]);
            selectOptions = speciesData.map((e) => e.name);
            allSpecies = metaData.map((e) => e.species);
        } catch (error) {
            console.error("Error fetching data:", error);
        } finally {
            isLoading = false;
        }
    }

    function handleInput(event) {
        species = event.target.value;
        updateSuggestions();
    }

    function handleSelectInput(event) {
        selected = event.target.value;
        updateSelectSuggestions();
    }

    function updateSuggestions() {
        if (species) {
            suggestions = allSpecies.filter((item) =>
                item.toLowerCase().includes(species.toLowerCase()),
            );
        } else {
            suggestions = [];
        }
    }

    function updateSelectSuggestions() {
        if (selected) {
            selectSuggestions = selectOptions.filter((item) =>
                item.toLowerCase().includes(selected.toLowerCase()),
            );
        } else {
            selectSuggestions = [];
        }
    }

    function handleSuggestionClick(suggestion) {
        species = suggestion;
        selectedSpecies.update(() => suggestion);
        selected = "";
        suggestions = [];
        debouncedFetchData();
    }

    function handleSelectSuggestionClick(select) {
        selected = select;
        selectSuggestions = [];
    }

    async function Search_SCONablesite(species, selected) {
        sconable = await load(
            `sconable_site_count_by_transcript?species=${species}&ensemble_rev=109&gene=${selected}`,
        );
        exoninfo = await load(
            `sconable_sites_group?species=${species}&ensemble_rev=109&gene=${selected}`,
        );
        sconable.rows.forEach((item) => {
            Object.values(item).forEach((value) => {
                if (
                    typeof value === "number" &&
                    (maxVal === null || value > maxVal)
                ) {
                    maxVal = value;
                }
            });
        });
        console.log(maxVal);
        sconable_columns = Object.keys(sconable.rows[0]);
    }

    function chunkArray(array, chunkSize) {
        const results = [];
        for (let i = 0; i < array.length; i += chunkSize) {
            results.push(array.slice(i, i + chunkSize));
        }
        return results;
    }

    async function Search_ExonInfo(cexon, ctranscript) {
        console.log("param", cexon, ctranscript);
        cexoninfo = exoninfo.filter(
            (v) => v.Exon === cexon && v.Transcript === ctranscript,
        );
        clickedRows = new Array(maxVal).fill(false);
        console.log(cexoninfo);
        sequence = await load(
            `scon_sites_by_transcript?species=${species}&ensemble_rev=109&exon=${cexon}&transcript=${ctranscript}`,
        );
        console.log(sequence);
        chunkedSeq = chunkArray(sequence, 10);
    }
    let hoveredRow = null;
    let hoveredPAM = null;

    function handleRowMouseEnter(index, start, end, scon_sites) {
        hoveredRow = { index, start, end };
        hoveredPAM = scon_sites.map((c) => ({
            target_start: c.Tartget_start,
            target_end: c.Tartget_end,
        }));
        console.log(hoveredPAM, "hoveredPAM");
    }

    function handleRowMouseLeave() {
        hoveredRow = null;
        hoveredPAM = null;
    }

    function isPAMPosition(pos, PAM) {
        if (PAM) {
            return PAM.some(
                (site) =>
                    pos >= Number(site.target_start) &&
                    pos <= Number(site.target_end),
            );
        }
        return false;
    }

    function getClassForBackground(s, hoveredRow, hoveredPAM) {
        if (
            hoveredRow &&
            s.pos >= hoveredRow.start &&
            s.pos <= hoveredRow.end
        ) {
            return "bg-yellow-100";
        } else if (isPAMPosition(s.pos, hoveredPAM)) {
            return "bg-green-200";
        }
        return "";
    }

    onMount(() => {
        if (!selectedSpecies) {
            species = "";
            selected = "";
        }
        fetchData();
    });
</script>

<div class="p-3 w-full">
    <Heading class="p-5">SCON run</Heading>
    <div class="p-3 z-100">
        <P size="xl" weight="semibold">Search</P>
        <!--<div class="flex">
            <div class="relative">
                <Label for="species_input" class="mb-2">Species</Label>
                <input
                    type="text"
                    id="species_input"
                    bind:value={species}
                    required
                    on:input={handleInput}
                    class="block disabled:cursor-not-allowed disabled:opacity-50 rtl:text-right p-2.5 focus:border-green-400 focus:ring-green-400 dark:focus:border-green-400 dark:focus:ring-green-400 bg-gray-50 text-gray-900 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 border-gray-300 dark:border-gray-600 text-sm rounded-lg suggestions-list"
                />
                {#if suggestions.length > 0}
                    <ul
                        class="absolute suggestions-list bg-white border border-gray-300 mt-2 rounded-lg shadow-lg flex flex-col z-10"
                    >
                        {#each suggestions as suggestion}
                            <button
                                class="p-2 cursor-pointer hover:bg-gray-100"
                                on:click={() =>
                                    handleSuggestionClick(suggestion)}
                            >
                                {suggestion}
                            </button>
                        {/each}
                    </ul>
                {/if}-
            </div>
            <div class="ml-3">
                <Label for="select_input" class="mb-2">Genes</Label>
                <input
                    type="text"
                    id="select_input"
                    bind:value={selected}
                    required
                    on:input={handleSelectInput}
                    class="block rounded-e-none disabled:cursor-not-allowed disabled:opacity-50 rtl:text-right p-2.5 focus:border-green-400 focus:ring-green-400 dark:focus:border-green-400 dark:focus:ring-green-400 bg-gray-50 text-gray-900 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 border-gray-300 dark:border-gray-600 text-sm suggestions-list"
                />
                {#if selectSuggestions.length > 0}
                    <ul
                        class="absolute suggestions-list bg-white border border-gray-300 mt-2 rounded-lg shadow-lg flex flex-col z-10"
                    >
                        {#if isLoading}
                            <Spinner class="m-5" color="green" />
                        {:else}
                            {#each selectSuggestions as suggestion}
                                <button
                                    class="p-2 cursor-pointer hover:bg-gray-100"
                                    on:click={() =>
                                        handleSelectSuggestionClick(suggestion)}
                                >
                                    {suggestion}
                                </button>
                            {/each}
                        {/if}
                    </ul>
                {/if}
            </div>
        </div>
    </div>-->
        <form class="flex">
            <div class="relative">
                <input
                    type="text"
                    id="species_input"
                    bind:value={species}
                    required
                    placeholder="Search Species"
                    on:input={handleInput}
                    class="h-10 rounded-lg rounded-e-none block disabled:cursor-not-allowed disabled:opacity-50 rtl:text-right p-2.5 focus:border-green-400 focus:ring-green-400 dark:focus:border-green-400 dark:focus:ring-green-400 bg-green-500 text-white dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 border-gray-300 dark:border-gray-600 text-sm suggestion-list placeholder-white"
                />
                {#if suggestions.length > 0}
                    <ul
                        class="absolute suggestion-list bg-white border border-gray-300 mt-2 rounded-lg shadow-lg flex flex-col z-10"
                    >
                        {#each suggestions as suggestion}
                            <button
                                class="p-2 cursor-pointer hover:bg-gray-100"
                                on:click={() =>
                                    handleSuggestionClick(suggestion)}
                            >
                                {suggestion}
                            </button>
                        {/each}
                    </ul>
                {/if}
            </div>

            <div>
                <input
                    type="text"
                    id="select_input"
                    bind:value={selected}
                    required
                    placeholder="Search Gene"
                    on:input={handleSelectInput}
                    class="h-10 block border-l-0 disabled:cursor-not-allowed disabled:opacity-50 rtl:text-right p-2.5 focus:border-green-400 focus:ring-green-400 dark:focus:border-green-400 dark:focus:ring-green-400 bg-gray-50 text-gray-900 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 border-gray-300 dark:border-gray-600 text-sm suggestions-list"
                />
                {#if selectSuggestions.length > 0}
                    <ul
                        class="absolute suggestions-list bg-white border border-gray-300 mt-2 rounded-lg shadow-lg flex flex-col z-10"
                    >
                        {#if isLoading}
                            <Spinner class="m-5" color="green" />
                        {:else}
                            {#each selectSuggestions as suggestion}
                                <button
                                    class="p-2 cursor-pointer hover:bg-gray-100"
                                    on:click={() =>
                                        handleSelectSuggestionClick(suggestion)}
                                >
                                    {suggestion}
                                </button>
                            {/each}
                        {/if}
                    </ul>
                {/if}
            </div>
            <div>
                <button
                    on:click={() => Search_SCONablesite(species, selected)}
                    color="green"
                    class="h-10 rounded-s-none text-center font-medium focus-within:outline-none inline-flex items-center justify-center px-5 py-2.5 text-sm text-white bg-green-500 hover:bg-green-800 dark:bg-green-600 dark:hover:bg-green-700 rounded-lg h-10 rounded-s-none"
                >
                    <SearchOutline />
                </button>
            </div>
        </form>
    </div>
    <div class="p-3">
        <P size="xl" weight="semibold" class="py-3">SCONable sites</P>
        {#if sconable}
            <Table class="overflow-x-scroll w-full outer-table">
                <TableHead>
                    {#each sconable.columns as s, i}
                        {#if s === "Exon"}
                            <TableHeadCell>{s}</TableHeadCell>
                        {:else}
                            <TableHeadCell>
                                <A
                                    href={`https://asia.ensembl.org/${species}/Transcript/Summary?t=${s}`}
                                    target="_blank"
                                    class="underline hover:no-underline">{s}</A
                                >
                            </TableHeadCell>
                        {/if}
                    {/each}
                </TableHead>
                <TableBody tableBodyClass="divide-y">
                    {#each sconable.rows as k, i}
                        <TableBodyRow>
                            {#each sconable.columns as c, j}
                                {#if k[c] === null}
                                    <TableBodyCell>0</TableBodyCell>
                                {:else if c !== "Exon"}
                                    <th
                                        on:click={() =>
                                            Search_ExonInfo(k.Exon, c)}
                                        class="px-6 py-4 whitespace-nowrap font-medium text-gray-900 dark:text-white cursor-pointer hover:bg-gray-100"
                                        >{k[c]}</th
                                    >
                                {:else}
                                    <TableBodyCell>{k[c]}</TableBodyCell>
                                {/if}
                            {/each}
                        </TableBodyRow>
                    {/each}
                </TableBody>
            </Table>
        {/if}
    </div>
    <div class="p-3">
        <P size="xl" weight="semibold" class="py-3">Exon Info</P>
        <Table class="overflow-x-scroll">
            <TableHead>
                <TableHeadCell>Gene</TableHeadCell>
                <TableHeadCell>Transcript</TableHeadCell>
                <TableHeadCell>Exon</TableHeadCell>
                <TableHeadCell>Exon_usage</TableHeadCell>
                <TableHeadCell>Exon_size</TableHeadCell>
                <TableHeadCell>Exon_strand</TableHeadCell>
                <TableHeadCell>Chromosome</TableHeadCell>
                <TableHeadCell>Exon_start</TableHeadCell>
                <TableHeadCell>Exon_end</TableHeadCell>
                <TableHeadCell>cum_size</TableHeadCell>
                <TableHeadCell>coding_size_t</TableHeadCell>
            </TableHead>
            {#if cexoninfo}
                <TableBody tableBodyClass="divide-y">
                    <TableBodyRow>
                        <TableBodyCell>{cexoninfo[0].Gene}</TableBodyCell>
                        <TableBodyCell>{cexoninfo[0].Transcript}</TableBodyCell>
                        <TableBodyCell>{cexoninfo[0].Exon}</TableBodyCell>
                        <TableBodyCell>{cexoninfo[0].Exon_usage}</TableBodyCell>
                        <TableBodyCell>{cexoninfo[0].Exon_size}</TableBodyCell>
                        <TableBodyCell>{cexoninfo[0].Exon_strand}</TableBodyCell
                        >
                        <TableBodyCell>{cexoninfo[0].Chromosome}</TableBodyCell>
                        <TableBodyCell>{cexoninfo[0].Exon_start}</TableBodyCell>
                        <TableBodyCell>{cexoninfo[0].Exon_end}</TableBodyCell>
                        <TableBodyCell>{cexoninfo[0].cum_size}</TableBodyCell>
                        <TableBodyCell
                            >{cexoninfo[0].coding_size_t}</TableBodyCell
                        >
                    </TableBodyRow>
                </TableBody>
            {/if}
        </Table>
    </div>
    <div class="p-3 z-0 w-full">
        <P size="xl" weight="semibold" class="py-3">SCONable site list</P>
        <div class="p-3 flex flex-wrap font-mono text-[15px] w-[calc(150*1ch)]">
            {#if sequence && cexoninfo && chunkedSeq}
                {#each chunkedSeq as chunk}
                    <div class="whitespace-pre">
                        {#each chunk as s, i}
                            <span
                                class="inline-block w-[1ch] {getClassForBackground(
                                    s,
                                    hoveredRow,
                                    hoveredPAM,
                                )}"
                                class:font-bold={hoveredRow &&
                                    s.pos >= hoveredRow.start &&
                                    s.pos <= hoveredRow.end}
                                class:text-emerald-400={s.className.includes(
                                    "exon",
                                ) && s.className.includes("left-pam")}
                                class:text-emerald-800={s.className.includes(
                                    "exon",
                                ) && s.className.includes("right-pam")}
                                class:text-red-700={s.className.includes(
                                    "exon",
                                ) && s.className.includes("scon_MAGR")}
                            >
                                {s.base}
                            </span>
                        {/each}
                    </div>
                {/each}
            {/if}
        </div>
        <Table class="w-full">
            <TableHead>
                <TableHeadCell>n_editable</TableHeadCell>
                <TableHeadCell>Insertion_sequence</TableHeadCell>
                <TableHeadCell>Insertion_start</TableHeadCell>
                <TableHeadCell>Insertion_end</TableHeadCell>
                <TableHeadCell>Left_remain</TableHeadCell>
                <TableHeadCell>Right_remain</TableHeadCell>
                <TableHeadCell>GC</TableHeadCell>
                <TableHeadCell>Self_complement</TableHeadCell>
                <TableHeadCell>relative_position</TableHeadCell>
                <TableHeadCell>n_editable</TableHeadCell>
                <TableHeadCell>sconIndex</TableHeadCell>
            </TableHead>

            {#if sequence && cexoninfo}
                {#each cexoninfo as c, i}
                    <TableBody tableBodyClass="divide-y w-full">
                        <tr
                            on:blur={handleRowMouseLeave}
                            on:focus={() =>
                                handleRowMouseEnter(
                                    i,
                                    c.Insertion_start,
                                    c.Insertion_end,
                                )}
                            on:mouseover={() =>
                                handleRowMouseEnter(
                                    i,
                                    c.Insertion_start,
                                    c.Insertion_end,
                                    c.scon_sites,
                                )}
                            on:mouseout={handleRowMouseLeave}
                        >
                            <td
                                on:click={() => toggleClick(i)}
                                class="px-6 py-4 whitespace-nowrap font-medium text-gray-900 dark:text-white cursor-pointer hover:bg-gray-100"
                            >
                                <ChevronDownOutline />
                            </td>
                            <TableBodyCell>{c.Insertion_sequence}</TableBodyCell
                            >
                            <TableBodyCell>{c.Insertion_start}</TableBodyCell>
                            <TableBodyCell>{c.Insertion_end}</TableBodyCell>
                            <TableBodyCell>{c.Left_remain}</TableBodyCell>
                            <TableBodyCell>{c.Right_remain}</TableBodyCell>
                            <TableBodyCell>{c.GC}</TableBodyCell>
                            <TableBodyCell>{c.Self_complement}</TableBodyCell>
                            <TableBodyCell>RELATIVE_POSITION</TableBodyCell>
                            <TableBodyCell>{c.n_editable}</TableBodyCell>
                            <TableBodyCell>SCONINDEX</TableBodyCell>
                        </tr>
                        {#if clickedRows[i]}
                            <TableBodyRow class="bg-gray-100">
                                <TableBodyCell colspan="11">
                                    <div class="inner-table-container">
                                        <Table class="inner-table">
                                            <TableHead>
                                                <TableHeadCell
                                                    >PAM_position</TableHeadCell
                                                >
                                                <TableHeadCell
                                                    >Target_sequence</TableHeadCell
                                                >
                                                <TableHeadCell
                                                    >Target_length</TableHeadCell
                                                >
                                                <TableHeadCell
                                                    >Target_start</TableHeadCell
                                                >
                                                <TableHeadCell
                                                    >Target_end</TableHeadCell
                                                >
                                                <TableHeadCell
                                                    >Left_remain</TableHeadCell
                                                >
                                                <TableHeadCell
                                                    >Right_remain</TableHeadCell
                                                >
                                                <TableHeadCell>GC</TableHeadCell
                                                >
                                                <TableHeadCell
                                                    >Self_complement</TableHeadCell
                                                >
                                                <TableHeadCell
                                                    >relative_position</TableHeadCell
                                                >
                                                <TableHeadCell
                                                    >mm_score</TableHeadCell
                                                >
                                            </TableHead>
                                            {#each c.scon_sites as ss}
                                                <TableBody
                                                    tableBodyClass="divide-y"
                                                >
                                                    <TableBodyRow>
                                                        <TableBodyCell
                                                            >{ss.PAM_position}</TableBodyCell
                                                        >
                                                        <TableBodyCell
                                                            >{ss.Target_sequence}</TableBodyCell
                                                        >
                                                        <TableBodyCell
                                                            >{ss.Target_length}</TableBodyCell
                                                        >
                                                        <TableBodyCell
                                                            >{ss.Tartget_start}</TableBodyCell
                                                        >
                                                        <TableBodyCell
                                                            >{ss.Tartget_end}</TableBodyCell
                                                        >
                                                        <TableBodyCell
                                                            >{ss.Left_remain}</TableBodyCell
                                                        >
                                                        <TableBodyCell
                                                            >{ss.Right_remain}</TableBodyCell
                                                        >
                                                        <TableBodyCell
                                                            >{ss.GC}</TableBodyCell
                                                        >
                                                        <TableBodyCell
                                                            >{ss.Self_complement}</TableBodyCell
                                                        >
                                                        <TableBodyCell
                                                            >relative_position</TableBodyCell
                                                        >
                                                        <TableBodyCell
                                                            >mm_score</TableBodyCell
                                                        >
                                                    </TableBodyRow>
                                                </TableBody>
                                            {/each}
                                        </Table>
                                    </div>
                                </TableBodyCell>
                            </TableBodyRow>
                        {/if}
                    </TableBody>
                {/each}
            {/if}
        </Table>
    </div>
</div>

<style>
    .suggestions-list {
        max-height: 150px;
        width: 500px;
        overflow-y: auto;
    }
    .suggestion-list {
        max-height: 150px;
        width: 280px;
        overflow-y: auto;
    }
    .placeholder-white::placeholder {
        color: white;
    }
    .inner-table-container {
        width: 100%;
        overflow-x: auto;
    }
    .inner-table {
        width: 100%;
        border-collapse: collapse;
    }
    .inner-table th,
    .inner-table td {
        border: 1px solid #e5e7eb;
        padding: 0.5rem;
    }
    .outer-table {
        width: 100%;
    }

    @import "https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css";
</style>
