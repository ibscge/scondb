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
        Radio,
        Checkbox,
        Popover,
        Button,
    } from "flowbite-svelte";
    import { selectedSpecies, push, selectedtype } from "../../lib/stores";
    import { load } from "../../lib/fetch";
    import { debounce } from "../../lib/utils";
    import { onMount, onDestroy } from "svelte";
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
    let selectedRadio;
    let lastSelected = "";
    let cachedSpeciesData = {};

    function toggleClick(index) {
        clickedRows[index] = !clickedRows[index];
        console.log("clickedRows", clickedRows);
    }

    let suggestions = [];
    let allSpecies = [];
    let selectSuggestions = [];
    let selectOptions = [];

    const debouncedFetchData = debounce(fetchData, 300);

    push.subscribe((value) => {
        console.log(value, "push_value");
        if (value) {
            selectedSpecies.subscribe((value) => {
                species = value;
            });
            selectedtype.subscribe((value) => {
                selectedRadio = value;
            });
            debouncedFetchData();
        } else {
            selectedSpecies.set(null);
        }
    });

    async function load_data(selectedRadio) {
        const metaData = await load(`meta/dataset?type=${selectedRadio}`);
        allSpecies = metaData.map((e) => e.species);
        //suggestions = allSpecies;
    }

    async function fetchData() {
        isLoading = true;
        if (species && !cachedSpeciesData[species]) {
            console.log("Fetching data for species:", species);
            const speciesData = await load(
                `sconable_genes?species=${species}&ensemble_rev=109&type=${selectedRadio}`,
            );
            cachedSpeciesData[species] = speciesData.map((e) => e.name);
        }
        console.log(cachedSpeciesData[species], species, "ggggggggg");
        selectOptions = cachedSpeciesData[species] || [];
        //selectSuggestions = selectOptions;
        isLoading = false;
    }

    function handleInput(event) {
        species = event.target.value;
        updateSuggestions();
    }

    const debouncedUpdateSelectSuggestions = debounce(
        updateSelectSuggestions,
        500,
    );

    function handleSelectInput(event) {
        const newSelected = event.target.value;
        if (newSelected !== lastSelected) {
            selected = newSelected;
            debouncedUpdateSelectSuggestions();
            lastSelected = newSelected;
        }
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
            const lowerSelected = selected.toLowerCase();
            selectSuggestions = selectOptions.filter((item) =>
                item.toLowerCase().includes(lowerSelected),
            );
        } else {
            selectSuggestions = [];
        }
        //console.log(selectSuggestions, "gggggg");
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
            `sconable_site_count_by_transcript?species=${species}&ensemble_rev=109&gene=${selected}&type=${selectedRadio}`,
        );
        console.log(sconable);
        exoninfo = await load(
            `sconable_sites_group?species=${species}&ensemble_rev=109&gene=${selected}&type=${selectedRadio}`,
        );
        console.log(exoninfo);
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
        const strand = Number(cexoninfo[0]?.Exon_strand) || 1;

        clickedRows = new Array(maxVal).fill(false);
        clickedRows[0] = true;
        console.log(cexoninfo);
        sequence = await load(
            `scon_sites_by_transcript?species=${species}&ensemble_rev=109&exon=${cexon}&transcript=${ctranscript}&type=${selectedRadio}`,
        );
        console.log(sequence, "seq");
        chunkedSeq = chunkArray(sequence, 10);
    }
    let hoveredRow = null;
    let hoveredPAM = null;

    function handleRowMouseEnter(index, start, end, scon_sites) {
        if (start > end) {
        [start, end] = [end, start];
        }

        hoveredRow = { index, start, end };

        hoveredPAM = scon_sites.map((c) => {
            let s = Number(c.Tartget_start);
            let e = Number(c.Tartget_end);
            if (s > e) [s, e] = [e, s];
            return {
                target_start: s,
                target_end: e,
            };
        });

        console.log(hoveredPAM, "hoveredPAM");
    }

    function handleRowMouseLeave() {
        hoveredRow = null;
        hoveredPAM = null;
    }

    function isPAMPosition(pos, PAM) {
        if (!PAM) return false;
        return PAM.some((site) =>
            site.target_start <= site.target_end
                ? pos >= Number(site.target_start) && pos <= Number(site.target_end)
                : pos >= Number(site.target_end) && pos <= Number(site.target_start),
        );
    }

    function getClassForBackground(s, hoveredRow, hoveredPAM) {
        if (!hoveredRow) return "";

        const inHighlight =
            hoveredRow.start <= hoveredRow.end
                ? s.pos >= hoveredRow.start && s.pos <= hoveredRow.end
                : s.pos >= hoveredRow.end && s.pos <= hoveredRow.start;

        const isHighlighted = inHighlight;
        const isTarget = isPAMPosition(s.pos, hoveredPAM);

        if (isHighlighted) return "bg-yellow-100";
        if (isTarget) return "bg-green-200";
        return "";
    }

    function handleRadioChange(value) {
        selectedRadio = value;
        species = "";
        selected = "";
    }
    $: {
        if (selectedRadio) {
            load_data(selectedRadio);
        }
    }
    onMount(() => {
        if (!selectedRadio) {
            selectedRadio = "MAGR";
        }
        load_data(selectedRadio);
        if (!species) {
            species = "";
            selected = "";
        }
    });
    $: chevronTrack = sequence
    ? (Number(cexoninfo[0]?.Exon_strand) === 1
        ? ">".repeat(sequence.length)
        : "<".repeat(sequence.length))
    : "";
</script>

<div class="p-3 w-full">
    <Heading class="p-5">SCON run</Heading>
    <div class="p-3 z-100">
        <P size="xl" weight="semibold">Search</P>
        <div class="p-3">
            <Radio
                name="radio"
                color="green"
                bind:group={selectedRadio}
                value="MAGR"
                on:change={() => handleRadioChange("MAGR")}
            >
                MAGR
            </Radio>
            <Radio
                name="radio"
                color="green"
                bind:group={selectedRadio}
                value="VDGN"
                on:change={() => handleRadioChange("VDGN")}
            >
                VDGN
            </Radio>
        </div>
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

            <div class="relative">
                <input
                    type="text"
                    id="select_input"
                    bind:value={selected}
                    required
                    placeholder="Search Gene"
                    on:input={handleSelectInput}
                    class="h-10 block border-l-0 disabled:cursor-not-allowed disabled:opacity-50 rtl:text-right p-2.5 focus:border-green-400 focus:ring-green-400 dark:focus:border-green-400 dark:focus:ring-green-400 bg-gray-50 text-gray-900 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 border-gray-300 dark:border-gray-600 text-sm suggestions-list"
                />
                {#if isLoading}
                    <Spinner
                        class="absolute right-0 top-0 m-2"
                        color="green"
                        size={6}
                    />
                {/if}{#if !isLoading && selectSuggestions.length > 0}
                    <ul
                        class="absolute suggestions-list bg-white border border-gray-300 mt-2 rounded-lg shadow-lg flex flex-col z-10"
                    >
                        {#each selectSuggestions as suggestion}
                            <button
                                class="p-2 cursor-pointer hover:bg-gray-100 z-10"
                                on:click={() =>
                                    handleSelectSuggestionClick(suggestion)}
                            >
                                {suggestion}
                            </button>
                        {/each}
                    </ul>{/if}
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
    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Gene"
        triggeredBy="#click"
        trigger="click"
        placement="top"
        reference="#click">The name of the gene containing the exon</Popover
    >
    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Transcript"
        triggeredBy="#click2"
        trigger="click"
        placement="top"
        reference="#click2"
        >The name of the transcript containing the exon
    </Popover>
    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Exon"
        triggeredBy="#click3"
        trigger="click"
        placement="top"
        reference="#click3">The unique name or number of the exon</Popover
    >
    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Exon usage"
        triggeredBy="#click4"
        trigger="click"
        placement="top"
        reference="#click4"
        >1 if the exon is included in all transcripts</Popover
    >
    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Exon size"
        triggeredBy="#click5"
        trigger="click"
        placement="top"
        reference="#click5">The length of the target exon (in bp)</Popover
    >
    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Exon strand"
        triggeredBy="#click6"
        trigger="click"
        placement="top"
        reference="#click6">The direction of the exon (e.g., + or -)</Popover
    >
    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Chromosome"
        triggeredBy="#click7"
        trigger="click"
        placement="top"
        reference="#click7"
        >The name of the chromosome where the exon is located</Popover
    >
    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Exon start"
        triggeredBy="#click8"
        trigger="click"
        placement="top"
        reference="#click8"
        >The start position of the exon (chromosomal coordinate)</Popover
    >
    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Exon end"
        triggeredBy="#click9"
        trigger="click"
        placement="top"
        reference="#click9"
        >The end position of the exon (chromosomal coordinate)</Popover
    >
    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Cumulative CDS size"
        triggeredBy="#click10"
        trigger="click"
        placement="top"
        reference="#click10"
        >Cumulative coding sequence length in the transcript up to the current
        exon</Popover
    >
    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Coding_size_T"
        triggeredBy="#click11"
        trigger="click"
        placement="top"
        reference="#click11"
        >The total coding sequence length of the transcript</Popover
    >

    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Insertion_sequence"
        triggeredBy="#click12"
        trigger="click"
        placement="top"
        reference="#click12"
        >Refers to the target sequence, either MAGR or VDGN</Popover
    >
    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Insertion_start"
        triggeredBy="#click13"
        trigger="click"
        placement="top"
        reference="#click13"
        >Start position of the target
    </Popover>
    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Insertion_end"
        triggeredBy="#click14"
        trigger="click"
        placement="top"
        reference="#click14">End position of the target</Popover
    >
    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Left_remain"
        triggeredBy="#click15"
        trigger="click"
        placement="top"
        reference="#click15"
        >Length of the remaining sequence on the left when the target is cut
        (e.g., MAG|R or VDG|N)</Popover
    >
    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Right_remain"
        triggeredBy="#click16"
        trigger="click"
        placement="top"
        reference="#click16"
        >Length of the remaining sequence on the right when the target is cut</Popover
    >

    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100"
        title="Self_complement"
        triggeredBy="#click18"
        trigger="click"
        placement="top"
        reference="#click18"
        >Number of possible occurrences where the CRISPR gRNA target sequence
        forms a secondary hairpin structure</Popover
    >
    <Popover
        arrow={false}
        class="w-64 text-sm font-light z-100 "
        title="n_editable"
        triggeredBy="#click19"
        trigger="click"
        placement="top"
        reference="#click19"
        >Number of CRISPR gRNA target sequences available for cutting the target</Popover
    >

    <div class="p-3">
        <P size="xl" weight="semibold" class="py-3">Exon Info</P>

        <Table divClass="-z-10">
            <TableHead>
                <TableHeadCell>
                    <div id="click">Gene</div></TableHeadCell
                >
                <TableHeadCell id="click2">Transcript</TableHeadCell>
                <TableHeadCell id="click3">Exon</TableHeadCell>
                <TableHeadCell id="click4">Exon_usage</TableHeadCell>
                <TableHeadCell id="click5">Exon_size</TableHeadCell>
                <TableHeadCell id="click6">Exon_strand</TableHeadCell>
                <TableHeadCell id="click7">Chromosome</TableHeadCell>
                <TableHeadCell id="click8">Exon_start</TableHeadCell>
                <TableHeadCell id="click9">Exon_end</TableHeadCell>
                <TableHeadCell id="click10">Cumulative CDS size</TableHeadCell>
                <TableHeadCell id="click11">coding_size_t</TableHeadCell>
            </TableHead>
            {#if cexoninfo}
                <TableBody tableBodyClass="divide-y">
                    <TableBodyRow>
                        <TableBodyCell>
                            {cexoninfo[0].Gene}
                        </TableBodyCell>
                        <TableBodyCell>
                            {cexoninfo[0].Transcript}
                        </TableBodyCell>
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

        <!--<div class="p-3 flex flex-wrap font-mono text-[15px] w-[calc(150*1ch)]">
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
            {/if}-->
        {#if sequence && cexoninfo}
            <div class="relative overflow-x-auto font-mono text-[15px] w-full">
              <div class="absolute top-0 left-0 flex">
                {#each sequence as _, i}
                  <span class="block w-[1ch] text-center text-gray-300">
                    {Number(cexoninfo[0]?.Exon_strand) === 1 ? ">" : "<"}
                  </span>
                {/each}
              </div>
          
              <div class="relative flex">
                {#each sequence as s}
                  <span
                    class="block w-[1ch] text-center"
                    class:font-bold={hoveredRow && s.pos >= hoveredRow.start && s.pos <= hoveredRow.end}
                    class:text-emerald-400={s.className.includes("exon") && s.className.includes("left-pam")}
                    class:text-emerald-800={s.className.includes("exon") && s.className.includes("right-pam")}
                    class:text-red-700={s.className.includes("exon") && s.className.includes("scon_MAGR")}
                  >
                    {s.base}
                  </span>
                {/each}
              </div>
            </div>
          {/if}
        <div class="max-h-[40rem] overflow-y-auto">
            <Table>
                <TableHead>
                    <TableHeadCell>n_editable</TableHeadCell>
                    <TableHeadCell id="click12"
                        >Insertion_sequence</TableHeadCell
                    >
                    <TableHeadCell id="click13">Insertion_start</TableHeadCell>
                    <TableHeadCell id="click14">Insertion_end</TableHeadCell>
                    <TableHeadCell id="click15">Left_remain</TableHeadCell>
                    <TableHeadCell id="click16">Right_remain</TableHeadCell>
                    <TableHeadCell id="click18">Self_complement</TableHeadCell>
                    <TableHeadCell id="click19">n_editable</TableHeadCell>
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
                                        Number(cexoninfo[0]?.Exon_strand || 1),
                                    )}
                                on:mouseout={handleRowMouseLeave}
                            >
                                <td
                                    on:click={() => toggleClick(i)}
                                    class="px-6 py-4 whitespace-nowrap font-medium text-gray-900 dark:text-white cursor-pointer hover:bg-gray-100"
                                >
                                    <ChevronDownOutline />
                                </td>
                                <TableBodyCell id="click12"
                                    >{c.Insertion_sequence}</TableBodyCell
                                >
                                <TableBodyCell id="click13"
                                    >{c.Insertion_start}</TableBodyCell
                                >
                                <TableBodyCell id="click14"
                                    >{c.Insertion_end}</TableBodyCell
                                >
                                <TableBodyCell id="click15"
                                    >{c.Left_remain}</TableBodyCell
                                >
                                <TableBodyCell id="click16"
                                    >{c.Right_remain}</TableBodyCell
                                >

                                <TableBodyCell id="click18"
                                    >{c.Self_complement}</TableBodyCell
                                >
                                <TableBodyCell id="click12"
                                    >{c.n_editable}</TableBodyCell
                                >
                            </tr>

                            {#if clickedRows[i]}
                                <TableBodyRow class="bg-gray-100">
                                    <TableBodyCell colspan="11">
                                        <div class="inner-table-container">
                                            <Table class="inner-table">
                                                <TableHead>
                                                    <TableHeadCell id="click20"
                                                        >PAM_position</TableHeadCell
                                                    >
                                                    <TableHeadCell id="click21"
                                                        >Target_sequence</TableHeadCell
                                                    >
                                                    <TableHeadCell id="click22"
                                                        >Target_length</TableHeadCell
                                                    >
                                                    <TableHeadCell id="click23"
                                                        >Target_start</TableHeadCell
                                                    >
                                                    <TableHeadCell id="click24"
                                                        >Target_end</TableHeadCell
                                                    >
                                                    <TableHeadCell
                                                        >Left_remain</TableHeadCell
                                                    >
                                                    <TableHeadCell
                                                        >Right_remain</TableHeadCell
                                                    >
                                                    <TableHeadCell id="click17"
                                                        >GC</TableHeadCell
                                                    >
                                                    <TableHeadCell
                                                        >Self_complement</TableHeadCell
                                                    >
                                                    <TableHeadCell id="click25"
                                                        >mm_score</TableHeadCell
                                                    >
                                                    <TableHeadCell
                                                        >in_frame</TableHeadCell
                                                    >
                                                </TableHead>
                                                <Popover
                                                    arrow={false}
                                                    class="w-72 text-sm font-light z-100 text-wrap"
                                                    title="PAM_position"
                                                    triggeredBy="#click20"
                                                    trigger="click"
                                                    placement="top"
                                                    reference="#click20"
                                                    >Position of the PAM
                                                    sequence relative to the
                                                    CRISPR gRNA target sequence</Popover
                                                >
                                                <Popover
                                                    arrow={false}
                                                    class="w-72 text-sm font-light z-100 text-wrap"
                                                    title="Target_sequence"
                                                    triggeredBy="#click21"
                                                    trigger="click"
                                                    placement="top"
                                                    reference="#click21"
                                                    >CRISPR gRNA target sequence</Popover
                                                >
                                                <Popover
                                                    arrow={false}
                                                    class="w-72 text-sm font-light z-100 text-wrap"
                                                    title="Target_length"
                                                    triggeredBy="#click22"
                                                    trigger="click"
                                                    placement="top"
                                                    reference="#click22"
                                                    >Length of the CRISPR gRNA
                                                    target sequence</Popover
                                                >
                                                <Popover
                                                    arrow={false}
                                                    class="w-72 text-sm font-light z-100 text-wrap"
                                                    title="Target_start"
                                                    triggeredBy="#click23"
                                                    trigger="click"
                                                    placement="top"
                                                    reference="#click23"
                                                    >Start position of the
                                                    CRISPR gRNA target sequence</Popover
                                                >
                                                <Popover
                                                    arrow={false}
                                                    class="w-72 text-sm font-light z-100 text-wrap"
                                                    title="Target_end"
                                                    triggeredBy="#click24"
                                                    trigger="click"
                                                    placement="top"
                                                    reference="#click24"
                                                    >End position of the CRISPR
                                                    gRNA target sequence</Popover
                                                >
                                                <Popover
                                                    arrow={false}
                                                    class="w-72 text-sm font-light z-100 text-wrap"
                                                    title="mm_score"
                                                    triggeredBy="#click25"
                                                    trigger="click"
                                                    placement="top"
                                                    reference="#click25"
                                                    >Mismatch score indicating
                                                    how frequently the CRISPR
                                                    gRNA target sequence maps to
                                                    the entire sequence</Popover
                                                >
                                                <Popover
                                                    arrow={false}
                                                    class="w-64 text-sm font-light z-100 text-wrap"
                                                    title="GC"
                                                    triggeredBy="#click17"
                                                    trigger="click"
                                                    placement="top"
                                                    reference="#click17"
                                                    >GC content of the CRISPR
                                                    gRNA target sequence for
                                                    cutting the target</Popover
                                                >
                                                {#each c.scon_sites as ss}
                                                    <TableBody
                                                        tableBodyClass="divide-y"
                                                    >
                                                        <tr class="bg-white">
                                                            <TableBodyCell
                                                                >{ss.PAM_position}</TableBodyCell
                                                            >
                                                            <td
                                                                class="px-6 py-4 whitespace-nowrap font-medium text-gray-900 dark:text-white"
                                                                on:blur={handleRowMouseLeave}
                                                                on:focus={() =>
                                                                    handleRowMouseEnter(
                                                                        i,
                                                                        c.Insertion_start,
                                                                        c.Insertion_end,
                                                                    )}
                                                                on:click={() =>
                                                                    handleRowMouseEnter(
                                                                        i,
                                                                        c.Insertion_start,
                                                                        c.Insertion_end,
                                                                        [
                                                                            {
                                                                                Tartget_start:
                                                                                    ss.Tartget_start,
                                                                                Tartget_end:
                                                                                    ss.Tartget_end,
                                                                            },
                                                                        ],
                                                                    )}
                                                                >{ss.Target_sequence}</td
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
                                                                >{ss.MM_score}</TableBodyCell
                                                            >
                                                            <TableBodyCell
                                                                >{ss[
                                                                    "3N"
                                                                ]}</TableBodyCell
                                                            >
                                                        </tr>
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
