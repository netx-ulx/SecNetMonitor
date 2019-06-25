#include "includes/input.p4"
#include "includes/headers.p4"
#include "includes/parser.p4"


field_list ipv4_checksum_list {
        ipv4.version;
        ipv4.ihl;
        ipv4.diffserv;
        ipv4.totalLen;
        ipv4.identification;
        ipv4.flags;
        ipv4.fragOffset;
        ipv4.ttl;
        ipv4.protocol;
        ipv4.srcAddr;
        ipv4.dstAddr;
}

field_list_calculation ipv4_checksum {
    input {
        ipv4_checksum_list;
    }
    algorithm : csum16;
    output_width : 16;
}

calculated_field ipv4.hdrChecksum  {
    verify ipv4_checksum;
    update ipv4_checksum;
}

/************************* Headers (metadata) *************************/
 
header_type custom_metadata_t {
    fields {
		full_hash: 32;
		target_column: 32;
		target_row: 32;
		target_slot: 32;
    }
}
metadata custom_metadata_t custom_metadata;

/************************* Field Lists *************************/

field_list hash_fields{
	ipv4.srcAddr;
	custom_metadata.target_row;
}

field_list_calculation hash{
	input{
		hash_fields;
	}
	algorithm: crc32;
	output_width: 32;
}


/************************* Routing Actions *************************/

action _drop() {
	drop();
}

action set_nhop(port) {
    modify_field(standard_metadata.egress_spec, port);
    add_to_field(ipv4.ttl, -1);
}

/************************* Routing Tables *************************/

table ipv4_lpm {
	reads {
		ipv4.dstAddr : lpm;
	}
	actions {
		set_nhop;
		_drop;
	}
	size: 1024;
}

/************************* Counters *************************/
// Multiple arrays of length width

counter counters{
	type: packets;
	instance_count: NUMBER_OF_INSTANCES;
	min_width: SLOT_SIZE;
	saturating; //prevents overflows
}

/************************* Update Actions *************************/

// Updates one row of the sketch
action update_row(){

	/*
		(0 + (hash_result % 2^64)) -> 2^64 so the module operation has no effect
	*/
	modify_field_with_hash_based_offset(custom_metadata.full_hash, 0, hash, 18446744073709551616);

	// get a position in the sketch_width range from the hash result 
	modify_field(custom_metadata.target_column, (custom_metadata.full_hash % SKETCH_WIDTH));
	
	// get the array index of the produced column position in the current row
	add(custom_metadata.target_slot, custom_metadata.target_column, custom_metadata.target_row); 

	// update that slot
	count(counters, custom_metadata.target_slot);

	// update current row (it works like an iterator)
    add_to_field(custom_metadata.target_row, SKETCH_WIDTH); 
}

/************************* Update Tables *************************/

table update_table1{
	actions{
		update_row;
	}
	size: 1;
}

table update_table2{
	actions{
		update_row;
	}
	size: 1;
}

table update_table3{
	actions{
		update_row;
	}
	size: 1;
}

table update_table4{
	actions{
		update_row;
	}
	size: 1;
}

table update_table5{
	actions{
		update_row;
	}
	size: 1;
}

table update_table6{
	actions{
		update_row;
	}
	size: 1;
}

table update_table7{
	actions{
		update_row;
	}
	size: 1;
}

table update_table8{
	actions{
		update_row;
	}
	size: 1;
}

table update_table9{
	actions{
		update_row;
	}
	size: 1;
}

table update_table10{
	actions{
		update_row;
	}
	size: 1;
}

table update_table11{
	actions{
		update_row;
	}
	size: 1;
}

table update_table12{
	actions{
		update_row;
	}
	size: 1;
}

table update_table13{
	actions{
		update_row;
	}
	size: 1;
}

table update_table14{
	actions{
		update_row;
	}
	size: 1;
}

table update_table15{
	actions{
		update_row;
	}
	size: 1;
}

table update_table16{
	actions{
		update_row;
	}
	size: 1;
}

table update_table17{
	actions{
		update_row;
	}
	size: 1;
}

table update_table18{
	actions{
		update_row;
	}
	size: 1;
}

table update_table19{
	actions{
		update_row;
	}
	size: 1;
}

table update_table20{
	actions{
		update_row;
	}
	size: 1;
}

/************************* Control *************************/

control ingress {
	
	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table1);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table2);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table3);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table4);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table5);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table6);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table7);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table8);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table9);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table10);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table11);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table12);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table13);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table14);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table15);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table16);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table17);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table18);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table19);

	if(custom_metadata.target_row <= LAST_ITERATION )
		apply(update_table20);

	// the sketch has a 20 rows maximum
	if(custom_metadata.target_row > LAST_ITERATION ) {
		apply(ipv4_lpm);
	}
}

control egress {
}
