import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

/* CompliantNode refers to a node that follows the rules (not malicious)*/
public class CompliantNode implements Node {

    private static final int ACCEPTED_LIMIT = 0;

    private final int numRounds;
    private int numRound = 0;
    private final Set<Integer> followersSet = new HashSet<>();
    private final Map<Transaction, AtomicInteger> seenTransactionsMap = new HashMap<>();

    public CompliantNode(double p_graph, double p_malicious, double p_txDistribution, int numRounds) {
        this.numRounds = numRounds;
    }

    public void setFollowees(boolean[] followees) {
        followersSet.addAll(IntStream.range(0, followees.length)
                .filter(index -> followees[index])
                .mapToObj(index -> index)
                .collect(Collectors.toSet()));
    }

    public void setPendingTransaction(Set<Transaction> pendingTransactions) {
        seenTransactionsMap.clear();
        seenTransactionsMap.putAll(pendingTransactions.stream().collect(Collectors.toMap(Function.identity(), t -> new AtomicInteger())));
    }

    public Set<Transaction> sendToFollowers() {
        return seenTransactionsMap.entrySet().stream()
                .filter(entry -> entry.getValue().intValue() >= (++numRound <= numRounds ? 0 : ACCEPTED_LIMIT))
                .map(Map.Entry::getKey)
                .collect(Collectors.toSet());
    }

    public void receiveFromFollowees(Set<Candidate> candidates) {
        for (Transaction tx : filterCandidates(candidates)) {
            if (seenTransactionsMap.containsKey(tx)) {
                seenTransactionsMap.get(tx).incrementAndGet();
            } else {
                seenTransactionsMap.put(tx, new AtomicInteger());
            }
        }
    }

    private Set<Transaction> filterCandidates(Set<Candidate> candidates) {
        return candidates.stream()
                .filter(candidate -> followersSet.contains(candidate.sender))
                .map(candidate -> candidate.tx)
                .collect(Collectors.toSet());
    }
}
