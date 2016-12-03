import java.util.*;
import java.security.PublicKey;

public class TxHandler {

    private final UTXOPool utxoPool;

    /**
     * Creates a public ledger whose current UTXOPool (collection of unspent transaction outputs) is
     * {@code utxoPool}. This should make a copy of utxoPool by using the UTXOPool(UTXOPool uPool)
     * constructor.
     */
    public TxHandler(UTXOPool utxoPool) {
        this.utxoPool = new UTXOPool(utxoPool);
    }

    /**
     * @return true if:
     * (1) all outputs claimed by {@code tx} are in the current UTXO pool, 
     * (2) the signatures on each input of {@code tx} are valid, 
     * (3) no UTXO is claimed multiple times by {@code tx},
     * (4) all of {@code tx}s output values are non-negative, and
     * (5) the sum of {@code tx}s input values is greater than or equal to the sum of its output
     *     values; and false otherwise.
     */
    public boolean isValidTx(Transaction tx) {
        // Checking condition partially 5
        double sumOfOutputs = 0; 
        for (int index = 0; index < tx.numOutputs(); index++) {
            Transaction.Output txOutput = tx.getOutput(index);
            if (txOutput.value < 0) {
                return false;
            } else {
                sumOfOutputs += txOutput.value;
            }
        }

        // Checking condition 1,2,3,4 & partially 5
        double sumOfInputs = 0;
        Map<PublicKey, Double> seenSpentOutputs = new HashMap<>();
        for (int index = 0; index < tx.numInputs(); index++) {
            Transaction.Input txInput = tx.getInput(index);
            UTXO assocUtxo = new UTXO(txInput.prevTxHash, txInput.outputIndex); 
            Transaction.Output assocOutput = utxoPool.getTxOutput(assocUtxo);
            if (assocOutput != null 
                && Crypto.verifySignature(assocOutput.address, tx.getRawDataToSign(index), txInput.signature)
                && (seenSpentOutputs.get(assocOutput.address) == null || seenSpentOutputs.get(assocOutput.address) != assocOutput.value)) {
                sumOfInputs += assocOutput.value;
                seenSpentOutputs.put(assocOutput.address, assocOutput.value);
            } else {
                return false; // Input not valid hence transaction is not valid
            }
        }
        
        // Checking condition 5
        return sumOfInputs >= sumOfOutputs;
    }

    /**
     * Handles each epoch by receiving an unordered array of proposed transactions, checking each
     * transaction for correctness, returning a mutually valid array of accepted transactions, and
     * updating the current UTXO pool as appropriate.
     */
    public Transaction[] handleTxs(Transaction[] possibleTxs) {
        List<Transaction> validTxs = new ArrayList<>();
        for (Transaction processedTx : possibleTxs) {
            if (isValidTx(processedTx)) {
                // Add to validTxs list
                validTxs.add(processedTx);
                // Update utxoPool
                for (int index = 0; index < processedTx.numInputs(); index++) {
                    Transaction.Input txInput = processedTx.getInput(index);
                    UTXO assocUtxo = new UTXO(txInput.prevTxHash, txInput.outputIndex);
                    utxoPool.removeUTXO(assocUtxo);
                }
                for (int index = 0; index < processedTx.numOutputs(); index++) {
                    utxoPool.addUTXO(new UTXO(processedTx.getHash(), index), processedTx.getOutput(index));
                }
            }
        }

        return validTxs.toArray(new Transaction[] {});
    }

}
